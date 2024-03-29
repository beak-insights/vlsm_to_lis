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
    SLEEP_SUBMISSION_COUNT,
    EXCLUDE_RESULTS,
    KEYWORDS_MAPPING,
    DEBUG_LOGGING
)
from db import engine, test_db_connection
from result_parser import ResultParser
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

    def patch_vlsm_error(self):
        logger.log("info", f"Hl7OrderHandler: Patching vlsm result-issues where length(raw_text) >= 1200")
        update_stmt = text(
            """update orders set lims_sync_status=5 where lims_sync_status=0 and length(raw_text) >= 1200"""
        )

        with Session(engine) as session:
            session.execute(update_stmt)
            session.commit()

    def fetch_hl7_results(self):
        logger.log("info", f"Hl7OrderHandler: Fetching hl7 result orders ...")
        select_stmt = text(
            """select * from orders where lims_sync_status=0""")

        with Session(engine) as session:
            result = session.execute(select_stmt)

        return self.hl7_result_to_dataframe(result.all(), result.keys())

    def hl7_result_to_dataframe(self, results, keys):
        # Aso skip those whose raw_data payload len is > 1200
        df = pd.DataFrame([self.sanitise(line)
                          for line in results], columns=keys)
        # df = df[df['raw_text'].map(lambda x: len(str(x)) < 1200)]
        return df

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
        logger.log("info", f"SenaiteConn: intiating connection to: {url}")
        try:
            response = self.session.post(url)
            if response.status_code == 200:
                logger.log(
                    "info", f"SenaiteConn: connection established")
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

    def resolve_by_keywords(self, keyword, results):
        orig = results
        if len(results) == 0:
            return False, None

        logger.log(
            "info", f"SenaiteHandler: Resolving analysis containing keyword {keyword} ...")

        mappings = KEYWORDS_MAPPING.get(keyword, [keyword])
        mappings.append(keyword)
        mappings = list(set(mappings))

        states = ["unassigned", "assigned"]
        results = list(filter(
            lambda r: r["review_state"] in states and r["getKeyword"] in mappings, results))

        if len(results) == 1:
            logger.log(
                "info", f"SenaiteHandler: Analysis with keyword {keyword} successfully resolved ...")
            return True, results[0]

        if len(results) > 1:
            logger.log(
                "info", f"SenaiteHandler: More than 1 anlysis found for keyword: {keyword}")
            return False, None

        logger.log(
            "info", f"SenaiteHandler: No anlysis found for keyword: {keyword} <> mappings: {mappings}")
        
        if DEBUG_LOGGING:
            for r in results:
                logger.log("info", f"filtered: getKeyword: {r['getKeyword']} <> status: {r['review_state']}")
            for r in orig:
                logger.log("info", f"orig: getKeyword: {r['getKeyword']} <> status: {r['review_state']}")
                
        return False, None

    def do_work_for_order(self, order_id, request_id, result, keyword=None):
        self._auth_session()

        searched, search_payload = self.search_analyses_by_request_id(
            request_id
        )

        if not searched:
            return False

        search_items = search_payload.get("items", [])

        found, search_data = self.resolve_by_keywords(keyword, search_items)
        if not found:
            logger.log(
                "info", f"SenaiteHandler: search for {request_id}, {keyword} did not find any matches")
            Hl7OrderHandler().update_hl7_result(order_id, 5)
            return False

        submitted = False
        submit_payload = {
            "transition": "submit",
            "Result": result,
            "InterimFields": []
        }

        logger.log("info", f"SenaiteHandler:  ---submitting result---")
        submitted, submission = self.update_resource(
            search_data.get("uid"), submit_payload
        )

        if not submitted:
            logger.log(
                "info", f"Submission Responce for checking :  {submission}")

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

            logger.log("info", f"SenaiteHandler:  ---verifying result---")
            verified, verification = self.update_resource(
                submission_data.get("uid"), verify_payload
            )

            # DateVerified is not None, 'VerifiedBy': 'system_daemon'
        return True


class ResultInterface(Hl7OrderHandler, SenaiteHandler):
    def run(self):

        if not test_db_connection():
            logger.log(
                "info", f"Failed to connect to db, backing off a little ...")
            return
        #self.patch_vlsm_error()

        if not self.test_senaite_connection():
            logger.log(
                "info", f"Failed to connect to Senaite, backing off a little ...")
            return

        logger.log("info", f"All connections were successfully established :)")

        to_exclude = [x.strip().lower() for x in EXCLUDE_RESULTS]
        orders = self.fetch_hl7_results()

        total = len(orders)

        if total <= 0:
            logger.log("info", f"ResultInterface: No orders at the moment :)")

        logger.log(
            "info", f"ResultInterface: {total} order are pending syncing ...")

        for index, order in orders.iterrows():

            if index > 0 and index % SLEEP_SUBMISSION_COUNT == 0:
                logger.log("info", f"ResultInterface:  ---sleeping---")
                time.sleep(SLEEP_SECONDS)
                logger.log("info", f"ResultInterface:  ---waking---")

            logger.log(
                "info", f"ResultInterface: Processing {index} of {total} ...")

            # Parse the result object before sending to LIMS
            result_parser = ResultParser(order["results"], order["test_unit"])
            result = str(result_parser.output)

            if isinstance(result, str):
                if result.strip().lower() in to_exclude:
                    # also update hl7 db for excluded to avoid unecessary trips
                    senaite_updated = True
                else:
                    senaite_updated = self.do_work_for_order(
                        order["id"],
                        order["order_id"],
                        result,
                        order["test_type"]
                    )
            else:
                senaite_updated = self.do_work_for_order(
                    order["id"],
                    order["order_id"],
                    result,
                    order["test_type"]
                )

            if senaite_updated:
                self.update_hl7_result(order["id"], 1)
