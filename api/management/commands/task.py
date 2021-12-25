import datetime
import logging

from django.conf import settings
from api.models import Subscription

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

logger = logging.getLogger(__name__)

def subs_status_check():
	get_subs = Subscription.objects.all()
	for i in get_subs:
		if i.enddate <= datetime.date.today():
			i.subscription_status = 'Expired'
			i.save()
		else:
			i.subscription_status = 'Active'
			i.save()


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
  """
  This job deletes APScheduler job execution entries older than `max_age` from the database.
  It helps to prevent the database from filling up with old historical records that are no
  longer useful.
  
  :param max_age: The maximum length of time to retain historical job execution records.
                  Defaults to 7 days.
  """
  DjangoJobExecution.objects.delete_old_job_executions(max_age)



class Command(BaseCommand):
	help = "Run APScheduler"

	def handle(self, *args, **options):
		scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
		scheduler.add_jobstore(DjangoJobStore(), "default")

		scheduler.add_job(
			subs_status_check,
			trigger=CronTrigger(day_of_week="mon-sun", hour="00", minute="00, 01, 02, 03, 04, 05"),  # Every 10 seconds
			id="subs_status_check",  # The `id` assigned to each job MUST be unique
			max_instances=1,
			replace_existing=True,
			)
		logger.info("Added job 'subs_status_check'.")

		scheduler.add_job(
			delete_old_job_executions,
	      trigger=CronTrigger(
	      	day_of_week="mon", hour="00", minute="00"
	        ),  # Midnight on Monday, before start of the next work week.
	      id="delete_old_job_executions",
	      max_instances=1,
	      replace_existing=True,
	      )
		logger.info(
			"Added weekly job: 'delete_old_job_executions'."
			)

		try:
			logger.info("Starting scheduler...")
			scheduler.start()
		except KeyboardInterrupt:
			logger.info("Stopping scheduler...")
			scheduler.shutdown()
			logger.info("Scheduler shut down successfully!")