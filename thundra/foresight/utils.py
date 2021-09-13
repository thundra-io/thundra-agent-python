import time

def current_milli_time():
    return round(time.time() * 1000)

def send_report_data(reporter, test_run_event):
    test_run_monitoring_data = test_run_event.get_monitoring_data()
    print(test_run_monitoring_data)
    reporter.send_reports([test_run_monitoring_data])