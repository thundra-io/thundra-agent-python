def send_report_data(reporter, test_run_event, api_key):
    test_run_monitoring_data = test_run_event.get_monitoring_data(api_key)
    reporter.send_reports([test_run_monitoring_data])