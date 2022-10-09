from spidermon import Monitor, monitors
from spidermon.core.suites import MonitorSuite
from spidermon.contrib.actions.slack.notifiers import SendSlackMessageSpiderFinished

@monitors.name('Item count')
class CustomItemCountMonitor(Monitor):

    @monitors.name('Minimum number of items')
    def test_minimum_number_of_items(self):
        item_extracted = getattr(
            self.data.stats, 'item_scraped_count', 0)
        minimum_threshold = 32

        msg = 'Extracted less than {} items'.format(
            minimum_threshold)
        self.assertTrue(
            item_extracted >= minimum_threshold, msg=msg
        )


class SpiderCloseMonitorSuite(MonitorSuite):
    monitors = [
        CustomItemCountMonitor, ## defined above
    ]

    monitors_finished_actions = [
        # actions to execute when suite finishes its execution
    ]

    monitors_failed_actions = [
        # actions to execute when suite finishes its execution with a failed monitor
    ]


class SpiderCloseMonitorSuite(MonitorSuite):
    monitors = [
        CustomItemCountMonitor,
    ]

    monitors_failed_actions = [
        SendSlackMessageSpiderFinished,
    ]