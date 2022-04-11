def to_minutes(local_time):
    local_time, meridian = local_time.split()
    hour, minutes = local_time.split('.')
    hour, minutes = int(hour), int(minutes)
    tot_minutes = hour * 60 + minutes
    if meridian == 'PM':
        tot_minutes += 60 * 12
    return tot_minutes


def from_minutes(time_in_minutes):
    return f"""{str(time_in_minutes // 60)}:{str(time_in_minutes % 60).zfill(2)} {'PM' if time_in_minutes >= (12 * 60)
    else 'AM'}"""


def refresh_states(time_in_minutes):
    global allotted_executive
    # For updating states
    for executive in executives_states:
        if executives_states[executive]['state'] == 'waiting' \
                and time_in_minutes > (executives_states[executive]['time'] + 15):
            executives_states[executive]['state'] = 'not_available'
        if executives_states[executive]['state'] == 'not_available' \
                and time_in_minutes > (executives_states[executive]['time'] + 45):
            executives_states[executive]['time'] = 0
            executives_states[executive]['state'] = 'available'

    # For updating executive_details
    temp_executives_record = {executive: {'trips': 0, 'delivery_charges': 0} for executive in executives_details}
    for record in delivery_history_db.values():
        temp_executives_record[record['executive']]['trips'] += 1
        temp_executives_record[record['executive']]['delivery_charges'] += record['delivery_charge']
    for executive in executives_details.keys():
        executives_details[executive]['allowance'] = temp_executives_record[executive]['trips'] * 10
        executives_details[executive]['delivery_charges'] = temp_executives_record[executive]['delivery_charges']
        executives_details[executive]['total'] = \
            executives_details[executive]['allowance'] + executives_details[executive]['delivery_charges']


def add_record(executive, pickup_time, delivery_time):
    global TRIP_NO
    if TRIP_NO not in delivery_history_db:
        record = {
            'trip': TRIP_NO,
            'executive': executive,
            'restaurant': restaurant,
            'destination': destination_point,
            'orders': 1,
            'pickup_time': pickup_time,
            'delivery_time': delivery_time,
            'delivery_charge': DELIVERY_CHARGE
        }
        delivery_history_db[TRIP_NO] = record
    else:
        delivery_history_db[TRIP_NO]['orders'] += 1
        delivery_history_db[TRIP_NO]['delivery_charge'] += 5


def display_available_executives():
    print("Available Executives:")
    print("Executive Delivery Charge Earned")
    for executive in executives_details:
        print(executive, executives_details[executive]['delivery_charges'])
    print("Allotted Delivery Executive: ", allotted_executive)


def book():
    global TRIP_NO
    time_in_minutes = to_minutes(time)
    refresh_states(time_in_minutes)
    global allotted_executive
    preferred_executive = 'DE1' if allotted_executive is None else allotted_executive
    found_waiting_executive = False

    for executive in executives_states:
        if executives_states[executive]['state'] == 'waiting' and \
                executives_states[executive]['destination'] == destination_point:
            found_waiting_executive = True
            if executives_details[executive]['delivery_charges'] < \
                    executives_details[preferred_executive]['delivery_charges']:
                preferred_executive = executive

    if not found_waiting_executive:
        for executive in executives_states:
            if executives_states[executive]['state'] == 'available':
                if executives_details[executive]['delivery_charges'] < \
                        executives_details[preferred_executive]['delivery_charges']:
                    preferred_executive = executive

    if preferred_executive != allotted_executive:
        executives_states[preferred_executive]['time'] = time_in_minutes
        executives_states[preferred_executive]['state'] = 'waiting'
        executives_states[preferred_executive]['destination'] = destination_point
        TRIP_NO += 1
        allotted_executive = preferred_executive
    assign_delivery_executive()


def assign_delivery_executive():
    pickup_time = from_minutes(to_minutes(time) + 15)
    delivery_time = from_minutes(to_minutes(time) + 45)
    add_record(allotted_executive, pickup_time, delivery_time)


def display_activities():
    time_in_minutes = to_minutes(time)
    refresh_states(time_in_minutes)
    # To display delivery history
    if len(delivery_history_db) > 0:
        print(*map(lambda x: x.upper(), delivery_history_db[TRIP_NO].keys()))
        for record in delivery_history_db.values():
            print(*record.values())
    else:
        print('NO HISTORY FOUND')

    # To Display total earned
    print('Executive', *map(lambda x: x.upper(), executives_details['DE1'].keys()))
    for executive in executives_details:
        print(executive, *executives_details[executive].values())


if __name__ == "__main__":
    no_of_delivery_executives = int(input("Enter number of delivery executives:"))
    NO_RESTAURANTS = 5  # count
    DROP_LOCATIONS = 5  # count
    DELIVERY_CHARGE = 50  # rupees
    ALLOWANCE_PER_TRIP = 10  # rupees
    TRIP_TIME = 30  # time in minutes
    TRIP_NO = 0

    allotted_executive = None

    executives_details = {
        f"DE{ctr}": {
            'allowance': 0,
            'delivery_charges': 0,
            'total': 0
        }
        for ctr in range(1, no_of_delivery_executives + 1)
    }

    # possible states are available waiting not-available
    executives_states = {
        f"DE{ctr}": {'state': 'available', 'time': 0, 'destination': ''} for ctr in
        range(1, no_of_delivery_executives + 1)
    }

    delivery_history_db = {}

    no_of_orders = int(input("Enter number of inputs:"))

    for ctr in range(no_of_orders):
        C_ID = int(input("Customer ID:"))
        restaurant = input("Restaurant:").strip()
        destination_point = input("Destination Point:").strip()
        time = input("Time:").strip()
        book()
        print(f"Booking ID: {TRIP_NO}")
        display_available_executives()

    display_activities()
