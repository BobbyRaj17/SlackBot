import pypd


# create an event
def pager_create_event():
    pypd.EventV2.create(data={
        'routing_key': '<pagerduty integration key>',
        'event_action': 'trigger',
        'payload': {
            'summary': 'This is an Test Error Event!',
            'severity': 'error',
            'source': 'pypd bot',
        }
    })
    return "Event created"
