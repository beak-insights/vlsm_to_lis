import ssl
import json
import time
import pandas as pd
from datetime import datetime
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth
from sqlalchemy import text
from sqlalchemy.orm import Session
from config import (
    SENAITE_BASE_URL,
    SENAITE_USER,
    SENAITE_PASSWORD,
    VERIFY_RESULT,
    SLEEP_SECONDS,
    SLEEP_SUBMISSION_COUNT
)
from db import engine, test_db_connection
from logger import Logger

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logger = Logger(__name__, __file__)


class Hl7OrderHandler:

    @staticmethod
    def sanitise(incoming):
        incoming = list(incoming)
        for index, item in enumerate(incoming):
            if isinstance(item, str):
                incoming[index] = item.replace(';', ' ').strip()
        return incoming

    def fetch_hl7_results(self):
        logger.log("info", f"Hl7OrderHandler: Fetching hl7 result orders ...")
        select_stmt = text("""select * from orders where lims_sync_status=0""")

        with Session(engine) as session:
            result = session.execute(select_stmt)

        return self.hl7_result_to_dataframe(result.all(), result.keys())

    def hl7_result_to_dataframe(self, results, keys):
        return pd.DataFrame([self.sanitise(line) for line in results], columns=keys)

    @staticmethod
    def hl7_result_to_csv(data_frame):
        data_frame.to_csv("hl7_results.csv", index=False)

    @staticmethod
    def update_hl7_result(order_id: int, lims_sync_status: int):
        logger.log(
            "info", f"Hl7OrderHandler: Updating hl7 result order with uid: {order_id} with lims_sync_status: {lims_sync_status} ...")
        update_stmt = text(
            """update orders set lims_sync_status = :status, lims_sync_date_time = :date_updated where id = :id""")

        update_line = {
            "id": order_id,
            "status": lims_sync_status,
            "date_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with Session(engine) as session:
            session.execute(update_stmt, update_line)
            session.commit()


class SenaiteHandler:
    def __init__(self):
        self.username = SENAITE_USER
        self.password = SENAITE_PASSWORD
        self.base_url = SENAITE_BASE_URL
        self.also_verify = VERIFY_RESULT

    def _auth_session(self):
        """ start a fresh requests session """
        self.session = requests.session()
        self.session.verify = ssl.CERT_NONE
        self.session.auth = HTTPBasicAuth(self.username, self.password)

    def test_senaite_connection(self) -> bool:
        self._auth_session()
        url = f"{self.base_url}"
        try:
            response = self.session.post(url)
            if response.status_code == 200:
                logger.log("info", f"SenaiteConn: connection established")
                return True
            else:
                logger.log("error", f"SenaiteConn: connection failed")
                self.error_handler(None, url, response)
                return False
        except Exception as e:
            logger.log(
                "error", f"SenaiteConn: connection failed with error: {e}")
            return False

    @staticmethod
    def error_handler(action=None, url=None, res=None):
        logger.log(
            "info", f"SenaiteHandler: Error Status Code: {res.status_code} Reason: {res.reason}")
        if action:
            logger.log(
                "info", f"SenaiteHandler: Error Resource ({action}) {url}")
        logger.log("info", f"SenaiteHandler: Error Detail {res.text}")

    @staticmethod
    def decode_response(response):
        return json.loads(response)

    def search_analyses_by_request_id(self, request_id):
        """Searches senaite's Analysis portal for results 
        @param request_id: Sample ID e.g BP-XXXXX
        @return dict
        """
        # searching using an ID.
        search_url = f"{self.base_url}search?getRequestID={request_id}&catalog=bika_analysis_catalog"
        logger.log(
            "info", f"SenaiteHandler: Searching for analysis with getRequestID {request_id}")
        response = self.session.get(search_url)
        if response.status_code == 200:
            data = self.decode_response(response.text)
            return True, data
        else:
            self.error_handler("search_analyses_by_csid", search_url, response)
            return False, None

    def update_resource(self, uid, payload):
        """ create a new resource in senaite: single or bundled """
        url = f"{self.base_url}update/{uid}"
        logger.log("info", f"SenaiteHandler: Updating resource: {url}")
        response = self.session.post(url, json=payload)
        if response.status_code == 200:
            data = self.decode_response(response.text)
            return True, data
        else:
            self.error_handler("create", url, response)
            return False, None

    def do_work_for_order(self, request_id, result, keyword=None):
        self._auth_session()

        searched, search_payload = self.search_analyses_by_request_id(
            request_id)
        # 'getResult': '', 'getResultCaptureDate': None, 'getSubmittedBy': None, 'getKeyword': 'XXXXXXX'

        submitted = False
        submit_payload = {
            "transition": "submit",
            "Result": result,
            "InterimFields": []
        }

        if not searched:
            return False

        search_items = search_payload.get("items")
        if not len(search_items) > 0:
            return False

        search_data = search_items[0]
        assert search_data.get("getParentTitle") == request_id

        logger.log("info", f"SenaiteHandler:  ---submission---")
        submitted, submission = self.update_resource(
            search_data.get("uid"), submit_payload)
        # Result is not None
        # 'SubmittedBy': 'system_daemon', ResultCaptureDate is not None, DateSubmitted == ResultCaptureDate

        if self.also_verify:
            if not submitted:
                return False

            verified = False
            verify_payload = {"transition": "verify"}

            submission_items = submission.get("items")
            if not len(submission_items) > 0:
                return False

            submission_data = submission_items[0]
            assert submission_data.get("uid") == search_data.get("uid")

            logger.log("info", f"SenaiteHandler:  ---verification---")
            verified, verification = self.update_resource(
                submission_data.get("uid"), verify_payload
            )

            # DateVerified is not None, 'VerifiedBy': 'system_daemon'
        return True


class ResultInterface(Hl7OrderHandler, SenaiteHandler):
    def run(self):
        database_reachable = test_db_connection()
        if not self.test_senaite_connection() or not database_reachable:
            return

        orders = self.fetch_hl7_results()
        for index, order in orders.iterrows():

            if index > 0 and index % SLEEP_SUBMISSION_COUNT == 0:
                logger.log("info", f"ResultInterface:  ---sleeping---")
                time.sleep(SLEEP_SECONDS)
                logger.log("info", f"ResultInterface:  ---waking---")

            senaite_updated = self.do_work_for_order(
                order["order_id"], order["results"], order["test_type"]
            )
            if senaite_updated:
                self.update_hl7_result(order["id"], 1)
