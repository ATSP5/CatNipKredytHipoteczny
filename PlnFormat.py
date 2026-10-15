class PlnFormat:
    """Liczby po polsku: spacja tysięcy, przecinek dziesiętny."""

    def formatter(self) -> "PlnFormat":
        return self

    @staticmethod
    def num(value: float, decimals: int = 0) -> str:
        if value is None or value != value:
            return "—"
        if value in (float("inf"), float("-inf")):
            return "∞"
        return format(value, ",.%df" % decimals).replace(",", " ").replace(".", ",")

    @classmethod
    def zl(cls, value: float, decimals: int = 0) -> str:
        return cls.num(value, decimals) + " zł"

    @classmethod
    def pct(cls, value: float, decimals: int = 2) -> str:
        return cls.num(value, decimals) + "%"
