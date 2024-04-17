class CustomIndex:
    def __init__(
        self, start, end, before_transform=lambda x: x, after_transform=lambda x: x
    ):
        self.start = start
        self.end = end
        self.before_transform = before_transform
        self.after_transform = after_transform

    def __call__(self, data):
        if len(data) >= self.end:
            return self.after_transform(
                int(self.before_transform(data[self.start : self.end]), 2)
            )
        else:
            return None


class AisMessage:
    MESSAGE_ID = CustomIndex(0, 6)
    REPETITION_INDEX = CustomIndex(MESSAGE_ID.end, MESSAGE_ID.end + 2)
    USER_ID = CustomIndex(REPETITION_INDEX.end, REPETITION_INDEX.end + 30)

    def __init__(self, data):
        self.data = data

    def json(self):
        properties = [
            prop
            for prop in dir(self)
            if isinstance(getattr(self.__class__, prop, None), property)
        ]

        # Create a dictionary to hold the property values
        data = {}
        for prop in properties:
            data[prop] = getattr(self, prop)

        return data

    @property
    def message_id(self):
        return self.MESSAGE_ID(self.data)

    @property
    def repetition_index(self):
        return self.REPETITION_INDEX(self.data)

    @property
    def user_id(self):
        return self.USER_ID(self.data)

    @property
    def checksum(self):
        pass


class Transformations:
    @classmethod
    def coord(cls, x):
        if x[0] == "0":
            return x[1:]
        inverted_bits = "".join(["1" if bit == "0" else "0" for bit in x[1:]])
        return int(x[0], 2) * "-" + bin(int(inverted_bits, 2) + 1)


class PositionMessage(AisMessage):
    NAV_STATUS = CustomIndex(AisMessage.USER_ID.end, AisMessage.USER_ID.end + 4)
    TURN_RATE = CustomIndex(NAV_STATUS.end, NAV_STATUS.end + 8)
    SOG = CustomIndex(TURN_RATE.end, TURN_RATE.end + 10)
    POSITION_ACCURACY = CustomIndex(SOG.end, SOG.end + 1)
    LONGITUDE = CustomIndex(
        POSITION_ACCURACY.end,
        POSITION_ACCURACY.end + 28,
        before_transform=Transformations.coord,
    )
    LATITUDE = CustomIndex(
        LONGITUDE.end, LONGITUDE.end + 27, before_transform=Transformations.coord
    )
    COG = CustomIndex(LATITUDE.end, LATITUDE.end + 12)
    TRUE_HEADING = CustomIndex(COG.end, COG.end + 9)
    TIME_INDICATOR = CustomIndex(TRUE_HEADING.end, TRUE_HEADING.end + 6)
    SPECIAL_MANOEUVRE_INDICATOR = CustomIndex(
        TIME_INDICATOR.end, TIME_INDICATOR.end + 2
    )
    RESERVED = CustomIndex(
        SPECIAL_MANOEUVRE_INDICATOR.end, SPECIAL_MANOEUVRE_INDICATOR.end + 3
    )
    RAIM_FLAG = CustomIndex(RESERVED.end, RESERVED.end + 1)
    COMMUNICATION_STATE = CustomIndex(RAIM_FLAG.end, RAIM_FLAG.end + 19)
    CHECKSUM = COMMUNICATION_STATE.end

    @property
    def navigation_status(self):
        return self.NAV_STATUS(self.data)

    @property
    def turn_rate(self):
        return self.TURN_RATE(self.data)

    @property
    def sog(self):
        return self.SOG(self.data)

    @property
    def position_accuracy(self):
        return self.POSITION_ACCURACY(self.data)

    @property
    def longitude(self):
        return self.LONGITUDE(self.data) / 600000

    @property
    def latitude(self):
        return self.LATITUDE(self.data) / 600000

    @property
    def cog(self):
        return self.COG(self.data)

    @property
    def true_heading(self):
        return self.TRUE_HEADING(self.data)

    @property
    def time_indicator(self):
        return self.TIME_INDICATOR(self.data)

    @property
    def special_manoeuvre_indicator(self):
        return self.SPECIAL_MANOEUVRE_INDICATOR(self.data)

    @property
    def reserved(self):
        return self.RESERVED(self.data)

    @property
    def raim_flag(self):
        return self.RAIM_FLAG(self.data)

    @property
    def communication_state(self):
        return self.COMMUNICATION_STATE(self.data)

    @property
    def checksum(self):
        return self.CHECKSUM


class BaseStationReport(AisMessage):
    YEAR_UTC = CustomIndex(AisMessage.USER_ID.end, AisMessage.USER_ID.end + 14)
    MONTH_UTC = CustomIndex(YEAR_UTC.end, YEAR_UTC.end + 4)
    DAY_UTC = CustomIndex(MONTH_UTC.end, MONTH_UTC.end + 5)
    HOUR_UTC = CustomIndex(DAY_UTC.end, DAY_UTC.end + 5)
    MINUTE_UTC = CustomIndex(HOUR_UTC.end, HOUR_UTC.end + 6)
    SECOND_UTC = CustomIndex(MINUTE_UTC.end, MINUTE_UTC.end + 6)
    POSITION_ACCURACY = CustomIndex(SECOND_UTC.end, SECOND_UTC.end + 1)
    LONGITUDE = CustomIndex(POSITION_ACCURACY.end, POSITION_ACCURACY.end + 28)
    LATITUDE = CustomIndex(LONGITUDE.end, LONGITUDE.end + 27)
    DEVICE_TYPE = CustomIndex(LATITUDE.end, LATITUDE.end + 4)
    LONG_RANGE_BROADCAST_CONTROL = CustomIndex(DEVICE_TYPE.end, DEVICE_TYPE.end + 1)
    RESERVED = CustomIndex(
        LONG_RANGE_BROADCAST_CONTROL.end, LONG_RANGE_BROADCAST_CONTROL.end + 9
    )
    RAIM_FLAG = CustomIndex(RESERVED.end, RESERVED.end + 1)
    COMMUNICATION_STATE = CustomIndex(RAIM_FLAG.end, RAIM_FLAG.end + 19)

    @property
    def year_utc(self):
        return self.YEAR_UTC(self.data)

    @property
    def month_utc(self):
        return self.MONTH_UTC(self.data)

    @property
    def day_utc(self):
        return self.DAY_UTC(self.data)

    @property
    def hour_utc(self):
        return self.HOUR_UTC(self.data)

    @property
    def minute_utc(self):
        return self.MINUTE_UTC(self.data)

    @property
    def second_utc(self):
        return self.SECOND_UTC(self.data)

    @property
    def position_accuracy(self):
        return self.POSITION_ACCURACY(self.data)

    @property
    def longitude(self):
        return self.LONGITUDE(self.data)

    @property
    def latitude(self):
        return self.LATITUDE(self.data)

    @property
    def device_type(self):
        return self.DEVICE_TYPE(self.data)

    @property
    def long_range_broadcast_control(self):
        return self.LONG_RANGE_BROADCAST_CONTROL(self.data)

    @property
    def reserved(self):
        return self.RESERVED(self.data)

    @property
    def raim_flag(self):
        return self.RAIM_FLAG(self.data)

    @property
    def communication_state(self):
        return self.COMMUNICATION_STATE(self.data)


class StaticData(AisMessage):
    AIS_VERSION_INDICATOR = CustomIndex(
        AisMessage.USER_ID.end, AisMessage.USER_ID.end + 2
    )
    OMI_NUMBER = CustomIndex(AIS_VERSION_INDICATOR.end, AIS_VERSION_INDICATOR.end + 30)
    CALL_SIGN = CustomIndex(OMI_NUMBER.end, OMI_NUMBER.end + 42)
    NAME = CustomIndex(CALL_SIGN.end, CALL_SIGN.end + 120)
    SHIP_TYPE_AND_CARGO_TYPE = CustomIndex(NAME.end, NAME.end + 8)
    GLOBAL_DIMENSION_POSITION_REFERENCE = CustomIndex(
        SHIP_TYPE_AND_CARGO_TYPE.end, SHIP_TYPE_AND_CARGO_TYPE.end + 30
    )
    POSITION_DETERMINING_DEVICE_TYPE = CustomIndex(
        GLOBAL_DIMENSION_POSITION_REFERENCE.end,
        GLOBAL_DIMENSION_POSITION_REFERENCE.end + 4,
    )
    ETA = CustomIndex(
        POSITION_DETERMINING_DEVICE_TYPE.end, POSITION_DETERMINING_DEVICE_TYPE.end + 20
    )
    MAXIMUM_STATIC_DRAUGHT = CustomIndex(ETA.end, ETA.end + 8)
    DESTINATION = CustomIndex(
        MAXIMUM_STATIC_DRAUGHT.end, MAXIMUM_STATIC_DRAUGHT.end + 120
    )
    DTE = CustomIndex(DESTINATION.end, DESTINATION.end + 1)
    RESERVE = CustomIndex(DTE.end, DTE.end + 1)

    @property
    def ais_version_indicator(self):
        return self.AIS_VERSION_INDICATOR(self.data)

    @property
    def omi_number(self):
        return self.OMI_NUMBER(self.data)

    @property
    def call_sign(self):
        return self.CALL_SIGN(self.data)

    @property
    def name(self):
        return self.NAME(self.data)

    @property
    def ship_type_and_cargo_type(self):
        return self.SHIP_TYPE_AND_CARGO_TYPE(self.data)

    @property
    def global_dimension_position_reference(self):
        return self.GLOBAL_DIMENSION_POSITION_REFERENCE(self.data)

    @property
    def position_determining_device_type(self):
        return self.POSITION_DETERMINING_DEVICE_TYPE(self.data)

    @property
    def eta(self):
        return self.ETA(self.data)

    @property
    def maximum_static_draught(self):
        return self.MAXIMUM_STATIC_DRAUGHT(self.data)

    @property
    def destination(self):
        return self.DESTINATION(self.data)

    @property
    def dte(self):
        return self.DTE(self.data)

    @property
    def reserve(self):
        return self.RESERVE(self.data)


msg_types = {
    1: PositionMessage,
    2: PositionMessage,
    3: PositionMessage,
    4: BaseStationReport,
    5: StaticData,
}


def get_message(msg_type: int, data) -> AisMessage:
    return msg_types.get(msg_type, AisMessage)(data)
