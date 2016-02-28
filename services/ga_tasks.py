"""This module defines a number of tasks related to harvesting GA.

we use the same approach described in update_glus.py for harvesting

With the help of MarkEdmondson1234 we define a process that uses

https://github.com/igrigorik/ga-beacon

To collate data about the blogpost (& other activities) that we need
to track using the tool. These are collated in a single GA account
specifically created for the Experts Community that in turn powers
a Super Proxy destination we can query on a regular basis to update
the visit count


"""

import webapp2
import logging
from datetime import datetime, date, timedelta
import time

import json
import urllib
import urllib2
from urllib2 import Request, urlopen, URLError


from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from google.appengine.api import mail
from google.appengine.api import app_identity


from models import ActivityPost
from models import ActivityRecord
from models import ActivityMetaData
from models import Account
from models import ProductGroup
from models import activity_record as ar

from .utils import get_so_api_key
from .utils import VALID_ACCOUNT_TYPES


SP_ROOT = "https://sunholo-ga-superproxy-2.appspot.com/query?"
SP_ID = "id=ahlzfnN1bmhvbG8tZ2Etc3VwZXJwcm94eS0ychULEghBcGlRdWVyeRiAgICA2reXCgw"
SP_FORMAT = "&format=json"

class CronHarvestGA(webapp2.RequestHandler):

    """Creates tasks to get GA data for each gde."""

    def get(self):
        """Create tasks."""
        logging.info('crons/harvest_ga')

        accounts = Account.query()
        user_count = 0
        for account in accounts:
            # only process valid account types
            if account.type not in VALID_ACCOUNT_TYPES:
                continue
            # uncomment this for testing against Mark's / Patrick's accounts
            # Patrick
            if account.gplus_id != "117346385807218227082":
            # Mark
            # if account.gplus_id != "115064340704113209584":
                continue

            user_count += 1

            taskqueue.add(queue_name='gplus',
                          url='/tasks/harvest_ga',
                          params={'key': account.key.urlsafe()})

        logging.info(
            'crons/harvest_ga created tasks for {} users.'.format(user_count))


class TaskHarvestGA(webapp2.RequestHandler):

    """Gets GA data for a particular gde."""

    def post(self):
        """."""
        logging.info('tasks/harvest_so')

        # get the gde Account entity
        safe_key = self.request.get('key')
        gde = ndb.Key(urlsafe=safe_key).get()
        logging.info(gde)

        url = SP_ROOT + SP_ID + SP_FORMAT

        req = Request(url)
        res = urlopen(req).read()
        rows = json.loads(res)["rows"]
        logging.info(rows)

		# get the activities for the gde
        activities = ActivityRecord.query(ActivityRecord.gplus_id == gde.gplus_id)
        for activity in activities:
        	logging.info(activity.activity_link)
        	for row in rows:
        		count = row[1]
        		logging.info(count)
        		url = row[0]
        		logging.info(url)
        		url_parts = url.split("/")
        		logging.info(url_parts[1])
        		if url_parts[1] == gde.gplus_id:
        			logging.info('we have a match')
        			logging.info(url_parts[len(url_parts) - 1])
        			if url_parts[len(url_parts) - 1] in activity.activity_link:
        				logging.info('WINNER WINNER CHICKEN DINNER')





