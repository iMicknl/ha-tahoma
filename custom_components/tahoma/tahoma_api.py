"""
Connection to TaHoma API.

Connection to Somfy TaHoma REST API
"""

import json
import logging
import pprint
import traceback
import urllib.parse

import requests

BASE_URL = "https://tahomalink.com/enduser-mobile-web/enduserAPI/"  # /doc for API doc
BASE_HEADERS = {"User-Agent": "mine"}

_LOGGER = logging.getLogger(__name__)


class TahomaApi:
    """Connection to TaHoma API."""

    def __init__(self, userName, userPassword, **kwargs):
        """Initialize the TaHoma protocol.

        :param userName: TaHoma username
        :param userPassword: Password
        :param kwargs: Ignore, only for unit test reasons
        """
        self.__devices = {}
        self.__gateway = {}
        self.__location = {}
        self.__cookie = ""
        self.__logged_in = False
        self.__events_registration = None
        self.__username = userName
        self.__password = userPassword
        self.__setup = None
        self.login()

    def login(self):
        """Login to TaHoma API."""
        if self.__logged_in:
            return
        login = {"userId": self.__username, "userPassword": self.__password}
        header = BASE_HEADERS.copy()
        request = requests.post(
            BASE_URL + "login", data=login, headers=header, timeout=10
        )

        try:
            result = request.json()
        except ValueError as error:
            raise Exception(
                "Not a valid result for login, "
                + "protocol error: "
                + request.status_code
                + " - "
                + request.reason
                + "("
                + error
                + ")"
            )

        if "error" in result.keys():
            raise Exception("Could not login: " + result["error"])

        if request.status_code != 200:
            raise Exception(
                "Could not login, HTTP code: "
                + str(request.status_code)
                + " - "
                + request.reason
            )

        if "success" not in result.keys() or not result["success"]:
            raise Exception("Could not login, no success")

        cookie = request.headers.get("set-cookie")
        if cookie is None:
            raise Exception("Could not login, no cookie set")

        self.__cookie = cookie
        self.__logged_in = True
        return self.__logged_in

    def send_request(
        self, method, url: str, headers, data=None, timeout: int = 10, retries: int = 3
    ):
        """Wrap the http requests and retries.

        :param method: The method to use for the request: post, get, delete.
        :param url: The url to send the POST to.
        :param headers: The headers of the request.
        :param data: The data of the request.
        :param timeout: The timeout of the request.
        :param retries: Maximum number of retries.
        :return:
        """
        if not self.__logged_in:
            self.login()

        stack = pprint.pformat(traceback.extract_stack())
        if "asyncio" in stack:
            _LOGGER.warning("I/O stack trace:\n" + stack)
        request = method(url, headers=headers, data=data, timeout=timeout)
        if request.status_code == 200:
            try:
                result = request.json()
            except ValueError as error:
                raise Exception("Not a valid result, protocol error: " + str(error))
            return result
        elif retries == 0:
            raise Exception(
                "Maximum number of consecutive retries reached. Error is:\n"
                + request.text
            )
        else:
            self.send_request(method, url, headers, data, timeout, retries - 1)

    def get_user(self):
        """Get the user information from the server.

        :return: a dict with all the information
        :rtype: dict

        raises ValueError in case of protocol issues

        :Example:

          "creationTime": <time>,
          "lastUpdateTime": <time>,
          "userId": "<email for login>",
          "title": 0,
          "firstName": "<First>",
          "lastName": "<Last>",
          "email": "<contact email>",
          "phoneNumber": "<phone>",
          "mobilePhone": "<mobile>",
          "locale": "<two char country code>"

        :Warning:

        The type and amount of values in the dictionary can change any time.
        """
        header = BASE_HEADERS.copy()
        header["Cookie"] = self.__cookie

        result = self.send_request(
            requests.get, BASE_URL + "enduser/mainAccount", headers=header
        )

        return result

    def get_setup(self):
        """Load the setup from the server.

        Loads the configuration from the server, nothing will
        be returned. After loading the configuration the devices
        can be obtained through get_device and get_devices.
        Also location and gateway will be set through this
        method.

        raises ValueError in case of protocol issues

        :Seealso:

        - get_device
        - get_devices
        - location
        - gateway
        """
        header = BASE_HEADERS.copy()
        header["Cookie"] = self.__cookie

        result = self.send_request(requests.get, BASE_URL + "setup", headers=header)

        self.__setup = result
        self._get_setup(result)

    def _get_setup(self, result):
        """Process the results from the server."""
        self.__devices = {}

        if "devices" not in result.keys():
            raise Exception("Did not find device definition.")

        for device_data in result["devices"]:
            device = Device(self, device_data)
            self.__devices[device.url] = device

        self.__location = result["location"]
        self.__gateway = result["gateways"]

    @property
    def location(self):
        """Return the location information stored in your TaHoma box.

        When the configuration has been loaded via get_setup this
        method retrieves all the location details which have
        been saved for your TaHoma box.
        :return: a dict with all the information
        :rtype: dict
        :Example:
          "creationTime": <time>,
          "lastUpdateTime": <time>,
          "addressLine1": "<street>",
          "postalCode": "<zip>",
          "city": "<city>",
          "country": "<country>",
          "timezone": "Europe/<city>",
          "longitude": 2.343,
          "latitude": 48.857,
          "twilightMode": 2,
          "twilightCity": "<city>",
          "summerSolsticeDuskMinutes": 1290,
          "winterSolsticeDuskMinutes": 990,
          "twilightOffsetEnabled": False,
          "dawnOffset": 0,
          "duskOffset": 0

        :Warning:

        The type and amount of values in the dictionary can change any time.

        :Seealso:

        - get_setup
        """
        return self.__location

    @property
    def gateway(self):
        """Return information about your TaHoma box.

        When the configuration has been loaded via get_setup this
        method retrieves all  details your TaHoma box.

        :return: a list of all gateways with a dict per gateway with
        all the information
        :rtype: list

        :Example:

          [{
              "gatewayId": "1234-1234-1234",
              "type": 15,
              "placeOID": "12345678-1234-1234-1234-12345678",
              "alive": True,
              "timeReliable": True,
              "connectivity": {
                  "status": "OK",
                  "protocolVersion": "8"
              },
              "up-to-date": True,
              "functions": "INTERNET_AUTHORIZATION,SCENARIO_DOWNLOAD,
                SCENARIO_AUTO_LAUNCHING,SCENARIO_TELECO_LAUNCHING,
                INTERNET_UPLOAD,INTERNET_UPDATE,TRIGGERS_SENSORS",
              "mode": "ACTIVE"
          }]

        :Warning:

        The type and amount of values in the dictionary can change any time.

        :Seealso:

        - get_setup
        """
        return self.__gateway

    def get_devices(self):
        """Return all devices.

        Which have been found with last get_setup request.

        With a previous get_setup call the devices which have
        been found will be returned.

        :return: Returns a dictionary {device_url -> Device }
        :rtype: dict

        :Seealso:

        - get_setup
        """
        return self.__devices

    def get_device(self, url):
        """Return a particular device.

        Which have been found with the last get_setup request.

        :param url: The device URL of the device to be returned.
        :return: Return the device identified by url or None
        :rtype: Device

        :Seealso:

        - get_setup
        """
        return self.__devices[url]

    def apply_actions(self, name_of_action, actions):
        """Start to execute an action or a group of actions.

        This method takes a bunch of actions and runs them on your
        TaHoma box.

        :param name_of_action: the label/name for the action
        :param actions: an array of Action objects
        :return: the execution identifier  **************
        what if it fails
        :rtype: string

        raises ValueError in case of protocol issues

        :Seealso:

        - get_events
        - get_current_executions
        """
        header = BASE_HEADERS.copy()
        header["Cookie"] = self.__cookie
        header["Content-Type"] = "application/json"

        actions_serialized = []

        for action in actions:
            actions_serialized.append(action.serialize())

        data = {"label": name_of_action, "actions": actions_serialized}
        json_data = json.dumps(data, indent=None, sort_keys=True)

        result = self.send_request(
            requests.post, BASE_URL + "exec/apply", header, json_data
        )

        if "execId" not in result.keys():
            raise Exception("Could not run actions, missing execId.")

        return result["execId"]

    def get_events(self):
        """Return a set of events.

        Which have been occurred since the last call of this method.

        This method should be called regulary to get all occurring
        Events. There are three different Event types/classes
        which can be returned:

        - DeviceStateChangedEvent, if any device changed it's state
        due to an applied action or just because of other reasons
        - CommandExecutionStateChangedEvent, a executed command goes
        through several phases which can be followed
        - ExecutionStateChangedEvent, ******** todo

        :return: an array of Events or empty array
        :rtype: list

        raises ValueError in case of protocol issues

        :Seealso:

        - apply_actions
        - launch_action_group
        - get_history
        """
        header = BASE_HEADERS.copy()
        header["Cookie"] = self.__cookie

        if self.__events_registration is None:
            register_response = self.send_request(
                requests.post, BASE_URL + "events/register", header
            )

            self.__events_registration = register_response["id"]

        result = self.send_request(
            requests.post,
            BASE_URL + "events/" + self.__events_registration + "/fetch",
            headers=header,
        )

        return self._get_events(result)

    def _get_events(self, result):
        """Run unit tests."""
        events = []

        for event_data in result:
            event = Event.factory(event_data)

            if event is not None:
                events.append(event)

                if isinstance(event, DeviceStateChangedEvent):
                    # change device state
                    if self.__devices[event.device_url] is None:
                        raise Exception(
                            "Received device change "
                            + "state for unknown device '"
                            + event.device_url
                            + "'"
                        )

                    self.__devices[event.device_url].set_active_states(event.states)

        return events

    def get_current_executions(self):
        """Get all current running executions.

        :return: Returns a dict of running Executions or empty dict.
        :rtype: dict

        raises ValueError in case of protocol issues

        :Seealso:

        - apply_actions
        - launch_action_group
        - get_history
        """
        header = BASE_HEADERS.copy()
        header["Cookie"] = self.__cookie

        result = self.send_request(
            requests.get, BASE_URL + "exec/current", headers=header
        )

        executions = {}

        for execution_data in result:
            exe = Execution(execution_data)
            executions[exe.execution_id] = exe

        return executions

    def get_history(self):
        """Get history."""
        header = BASE_HEADERS.copy()
        header["Cookie"] = self.__cookie

        result = self.send_request(requests.get, BASE_URL + "history", headers=header)

        return result

    def cancel_all_executions(self):
        """Cancel all running executions.

        raises ValueError in case of any protocol issues.
        """
        header = BASE_HEADERS.copy()
        header["Cookie"] = self.__cookie

        self.send_request(
            requests.delete, BASE_URL + "exec/current/setup", headers=header
        )

    def get_action_groups(self):
        """Get all Action Groups.

        :return: List of Action Groups
        """
        header = BASE_HEADERS.copy()
        header["Cookie"] = self.__cookie

        request = requests.get(BASE_URL + "actionGroups", headers=header, timeout=10)

        if request.status_code != 200:
            self.__logged_in = False
            self.login()
            self.get_action_groups()
            return

        try:
            result = request.json()
        except ValueError:
            raise Exception("get_action_groups: Not a valid result for ")

        groups = []

        for group_data in result:
            group = ActionGroup(group_data)
            groups.append(group)

        return groups

    def launch_action_group(self, action_id):
        """Start action group."""
        header = BASE_HEADERS.copy()
        header["Cookie"] = self.__cookie

        result = self.send_request(
            requests.post, BASE_URL + "exec/" + action_id, headers=header
        )

        if "execId" not in result.keys():
            raise Exception("Could not launch action" + "group, missing execId.")

        return result["execId"]

    def get_states(self, devices):
        """Get States of Devices."""
        header = BASE_HEADERS.copy()
        header["Cookie"] = self.__cookie

        for device in devices:
            path = "setup/devices/" + urllib.parse.quote_plus(device.url) + "/states"
            result = self.send_request(requests.get, BASE_URL + path, headers=header)

            try:
                self.__devices[device.url].set_active_states(result)
            except KeyError:
                pass

    def refresh_all_states(self):
        """Update all states."""
        header = BASE_HEADERS.copy()
        header["Cookie"] = self.__cookie

        self.send_request(
            requests.post, BASE_URL + "setup/devices/states/refresh", headers=header
        )


class Device:
    """Represents an TaHoma Device."""

    def __init__(self, protocol, dataInput):
        """Initialize the TaHoma Device."""
        self.__protocol = protocol
        self.__raw_data = dataInput
        self.__active_states = {}

        debug_output = json.dumps(dataInput)

        if "label" not in dataInput.keys():
            raise ValueError("No device name found: " + debug_output)

        self.__label = dataInput["label"]

        if "controllableName" not in dataInput.keys():
            raise ValueError("No control label name found: " + debug_output)

        self.__type = dataInput["controllableName"]

        if "deviceURL" not in dataInput.keys():
            raise ValueError("No control URL: " + debug_output)

        self.__url = dataInput["deviceURL"]

        if "uiClass" not in dataInput.keys():
            raise ValueError("No ui Class: " + debug_output)

        self.__uiclass = dataInput["uiClass"]

        if "widget" not in dataInput.keys():
            raise ValueError("No widget: " + debug_output)

        self.__widget = dataInput["widget"]

        # Parse definitions

        if "definition" not in dataInput.keys():
            raise ValueError("No device definition found: " + debug_output)

        self.__definitions = {"commands": [], "states": []}

        definition = dataInput["definition"]

        if "commands" in definition.keys():
            for command in definition["commands"]:
                if command["commandName"] in self.__definitions["commands"]:
                    raise ValueError(
                        "Command '"
                        + command["commandName"]
                        + "' double defined - "
                        + debug_output
                    )

                self.__definitions["commands"].append(command["commandName"])

        if "states" in definition.keys():
            for state in definition["states"]:
                if state["qualifiedName"] in self.__definitions["states"]:
                    raise ValueError(
                        "State '"
                        + state["qualifiedName"]
                        + "' double defined - "
                        + debug_output
                    )

                self.__definitions["states"].append(state["qualifiedName"])

        self.__command_def = dataInput["definition"]["commands"]

        self.__states_def = dataInput["definition"]["states"]

        # Parse active states

        # calculate the amount of known active states
        active_states_amount = 0
        if "states" in dataInput.keys():
            for state in dataInput["states"]:
                active_states_amount += 1

        # make sure there are not more active states than definitions
        if active_states_amount > len(self.state_definitions):
            raise ValueError(
                "Mismatch of state definition and active states ("
                + str(len(self.state_definitions))
                + "/"
                + str(active_states_amount)
                + "): "
                + debug_output
            )

        if len(self.state_definitions) > 0:

            if "states" in dataInput.keys():
                # raise ValueError("No active states given.")

                for state in dataInput["states"]:

                    if state["name"] not in self.state_definitions:
                        raise ValueError(
                            "Active state '"
                            + state["name"]
                            + "' has not been defined: "
                            + debug_output
                        )

                    if state["name"] in self.__active_states.keys():
                        raise ValueError(
                            "Active state '"
                            + state["name"]
                            + "' has been double defined: "
                            + debug_output
                        )

                    self.__active_states[state["name"]] = state["value"]

    @property
    def label(self):
        """Label of device."""
        return self.__label

    @property
    def command_definitions(self):
        """List of command devinitions."""
        return self.__definitions["commands"]

    @property
    def state_definitions(self):
        """State of command devinition."""
        return self.__definitions["states"]

    @property
    def active_states(self):
        """Get active states."""
        return self.__active_states

    def set_active_state(self, name, value):
        """Set active state."""
        if name not in self.__active_states.keys():
            self.__active_states[name] = value

        if isinstance(self.__active_states[name], int) and isinstance(value, str):
            # we get an update as str but current value is
            # an int, try to convert
            self.__active_states[name] = int(value)
        elif isinstance(self.__active_states[name], float) and isinstance(value, str):
            # we get an update as str but current value is
            # a float, try to convert
            self.__active_states[name] = float(value)
        else:
            self.__active_states[name] = value

    def set_active_states(self, states):
        """Set active states to device."""
        for state in states:
            self.set_active_state(state["name"], state["value"])

    @property
    def type(self):
        """Get device type."""
        return self.__type

    @property
    def url(self):
        """Get device url."""
        return self.__url

    @property
    def uiclass(self):
        """Get device ui class."""
        return self.__uiclass

    @property
    def widget(self):
        """Get device widget type."""
        return self.__widget

    @property
    def command_def(self):
        """Get device widget type."""
        return self.__command_def

    @property
    def states_def(self):
        """Get device widget type."""
        return self.__states_def

    # def execute_action(self, action):
    #    """Exceute action."""
    #    self.__protocol


class Action:
    """Represents an TaHoma Action."""

    def __init__(self, data):
        """Initialize the TaHoma Action."""
        self.__commands = []

        if isinstance(data, dict):
            self.__device_url = data["deviceURL"]

            for cmd in data["commands"]:
                if "parameters" in cmd.keys():
                    self.__commands.append(Command(cmd["name"], cmd["parameters"]))
                else:
                    self.__commands.append(Command(cmd["name"]))
        elif isinstance(data, str):
            self.__device_url = data
        else:
            self.__device_url = ""

    @property
    def device_url(self):
        """Get device url of action."""
        return self.__device_url

    @device_url.setter
    def device_url(self, url):
        """Set device url of action."""
        self.__device_url = url

    def add_command(self, cmd_name, *args):
        """Add command to action."""
        self.__commands.append(Command(cmd_name, args))

    @property
    def commands(self):
        """Get commands."""
        return self.__commands

    def serialize(self):
        """Serialize action."""
        commands = []

        for cmd in self.commands:
            commands.append(cmd.serialize())

        out = {"commands": commands, "deviceURL": self.__device_url}

        return out

    def __str__(self):
        """Format to json."""
        return json.dumps(
            self.serialize(), indent=4, sort_keys=True, separators=(",", ": ")
        )

    def __repr__(self):
        """Format to json."""
        return json.dumps(
            self.serialize(), indent=None, sort_keys=True, separators=(",", ": ")
        )


class Command:
    """Represents an TaHoma Command."""

    def __init__(self, cmd_name, *args):
        """Initialize the TaHoma Command."""
        self.__name = cmd_name

        if len(args):
            for arg in args[0]:
                if (
                    isinstance(arg, str) is False
                    and isinstance(arg, int) is False
                    and isinstance(arg, float) is False
                ):
                    raise ValueError("Type '" + type(arg) + "' is not Int, bool or .")

            self.__args = args[0]
        else:
            self.__args = []

    @property
    def name(self):
        """Get name of command."""
        return self.__name

    @property
    def parameter(self):
        """Get parameter of command."""
        return self.__args

    def serialize(self):
        """Serialize command."""
        return {"name": self.__name, "parameters": self.__args}

    def __str__(self):
        """Format to json."""
        return json.dumps(
            self.serialize(), indent=4, sort_keys=True, separators=(",", ": ")
        )

    def __repr__(self):
        """Format to json."""
        return json.dumps(
            self.serialize(), indent=None, sort_keys=True, separators=(",", ": ")
        )


class ActionGroup:
    """Represents an TaHoma Action Group."""

    def __init__(self, data):
        """Initialize the TaHoma Action Group."""
        if hasattr(data, "lastUpdateTime"):
            self.__last_update = data["lastUpdateTime"]
        else:
            self.__last_update = -1
        self.__name = data["label"]
        self.__oid = data["oid"]

        self.__actions = []

        for cmd in data["actions"]:
            self.__actions.append(Action(cmd))

    @property
    def last_update(self):
        """Get last update."""
        return self.__last_update

    @property
    def name(self):
        """Get name of action group."""
        return self.__name

    @property
    def oid(self):
        """Get oid of the action group."""
        return self.__oid

    @property
    def actions(self):
        """Get list of actions."""
        return self.__actions


class Event:
    """Represents an TaHoma Event."""

    @staticmethod
    def factory(data):
        """TaHoma Event factory."""
        if data["name"] == "DeviceStateChangedEvent":
            return DeviceStateChangedEvent(data)
        elif data["name"] == "ExecutionStateChangedEvent":
            return ExecutionStateChangedEvent(data)
        elif data["name"] == "CommandExecutionStateChangedEvent":
            return CommandExecutionStateChangedEvent(data)
        else:
            print("Unknown event '" + data["name"] + "' occurred.")
            # raise ValueError("Unknown event '" + data['name'] + "' occurred.")
            return None


class DeviceStateChangedEvent(Event):
    """Represents an TaHoma DeviceStateChangedEvent."""

    def __init__(self, data):
        """Initialize the TaHoma DeviceStateChangedEvent."""
        self.__device_url = data["deviceURL"]
        self.__states = data["deviceStates"]

    @property
    def device_url(self):
        """Get device url."""
        return self.__device_url

    @property
    def states(self):
        """Get list of states."""
        return self.__states


class CommandExecutionStateChangedEvent(Event):
    """Represents an TaHoma CommandExecutionStateChangedEvent."""

    def __init__(self, data):
        """Initialize the TaHoma CommandExecutionStateChangedEvent."""
        self.__exec_id = data["execId"]
        self.__device_url = data["deviceURL"]

        try:
            self.__state = EventState(int(data["newState"]))
        except ValueError:
            self.__state = EventState.Unknown

        if self.__state == EventState.Failed:
            self.__failure_type = data["failureType"]
        else:
            self.__failure_type = None

    @property
    def exec_id(self):
        """Get exec id."""
        return self.__exec_id

    @property
    def device_url(self):
        """Get device url."""
        return self.__device_url

    @property
    def state(self):
        """Get state."""
        return self.__state

    @property
    def failure_type(self):
        """Get failure type."""
        return self.__failure_type


class ExecutionStateChangedEvent(Event):
    """Represents an TaHoma ExecutionStateChangedEvent."""

    def __init__(self, data):
        """Initialize the TaHoma ExecutionStateChangedEvent."""
        self.__exec_id = data["execId"]

        try:
            self.__state = EventState(int(data["newState"]))
        except ValueError:
            self.__state = EventState.Unknown

        if self.__state == EventState.Failed:
            self.__failure_type = data["failureType"]
            fail = data["failedCommands"]["command"]["deviceURL"]
            self.__failed_device_url = fail
        else:
            self.__failure_type = None
            self.__failed_device_url = None

    @property
    def exec_id(self):
        """Get exec id."""
        return self.__exec_id

    @property
    def state(self):
        """Get state."""
        return self.__state

    @property
    def failure_type(self):
        """Get failure url."""
        return self.__failure_type

    @property
    def failure_device_url(self):
        """Get failure device url."""
        return self.__failed_device_url


class EventState:
    """Represents an TaHoma EventState."""

    def __init__(self, state):
        """Initialize the TaHoma EventState."""
        if isinstance(state, int):
            if state is EventState.Unknown0:
                self.__state = EventState.Unknown0
            elif state is EventState.NotTransmitted:
                self.__state = EventState.NotTransmitted
            elif state is EventState.Unknown2:
                self.__state = EventState.Unknown2
            elif state is EventState.Unknown3:
                self.__state = EventState.Unknown3
            elif state is EventState.Completed:
                self.__state = EventState.Completed
            elif state is EventState.Failed:
                self.__state = EventState.Failed
            elif state is EventState.Unknown:
                self.__state = EventState.Unknown
            else:
                raise ValueError("Unknown state init " + str(state))
        elif isinstance(state, str):
            # more states are missing
            if state == "NOT_TRANSMITTED":
                self.__state = EventState.NotTransmitted
            elif state == "TRANSMITTED":
                self.__state = EventState.Transmitted
            elif state == "IN_PROGRESS":
                self.__state = EventState.InProgress
            elif state == "COMPLETED":
                self.__state = EventState.Completed
            elif state == "FAILED":
                self.__state = EventState.Failed
            else:
                raise ValueError("Unknown state init '" + state + "'")
        else:
            raise ValueError("EventState init can only be called with int or str.")

    @property
    def state(self):
        """Get state."""
        return self.__state

    def __int__(self):
        """Get int state."""
        return self.__state

    # python > 3
    def __eq__(self, other):
        """Compare State."""
        if isinstance(other, int):
            return self.__state == other
        if isinstance(other, EventState):
            return self.__state == other.state

        return False

    # several names still missing
    Unknown0 = 0
    NotTransmitted = 1
    Unknown2 = 2
    Unknown3 = 3
    Completed = 4
    Failed = 5
    Unknown = 6
    Transmitted = 11
    InProgress = 12


class Execution:
    """Represents an TaHoma Execution."""

    def __init__(self, data):
        """Initialize the TaHoma Execution."""
        self.__execution_id = data["id"]
        self.__start_time = data["startTime"]
        self.__state = EventState(data["state"])
        self.__name = data["actionGroup"]["label"]

        self.__actions = []

        for cmd in data["actionGroup"]["actions"]:
            self.__actions.append(Action(cmd))

    @property
    def execution_id(self):
        """Get id."""
        return self.__execution_id

    @property
    def start_time(self):
        """Get start time."""
        return self.__start_time

    @property
    def state(self):
        """Get state."""
        return self.__state

    @property
    def name(self):
        """Get name."""
        return self.__name

    @property
    def actions(self):
        """Get actions."""
        return self.__actions
