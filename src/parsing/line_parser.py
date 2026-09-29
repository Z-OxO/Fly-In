from src.models import Zone, MapError, Hub, Link, HubType

ALLOWED: dict[str, frozenset[str]] = {
    "nb_drones": frozenset(),
    "hub": frozenset({"zone", "color", "max_drones"}),
    "start_hub": frozenset({"zone", "color", "max_drones"}),
    "end_hub": frozenset({"zone", "color", "max_drones"}),
    "connection": frozenset({"max_link_capacity"}),
}


class LineParser:
    """Parse one line of a map file."""

    def __init__(self, linenum: int, text: str):
        """Store the line to parse.

        Args:
            linenum: Line number, used in errors.
            text: Line content, without comment.
        """
        self._linenum = linenum
        self._text = text

    def _error(self, msg: str) -> MapError:
        """Return a MapError for the current line."""
        return MapError(self._linenum, msg)

    def _get_zone(self, metadata: dict[str, str]) -> Zone:
        """Read the zone from the metadata.

        Args:
            metadata: Parsed metadata.

        Returns:
            The zone, normal by default.

        Raises:
            MapError: If the zone is unknown.
        """
        raw_zone = metadata.get("zone", "normal")
        try:
            zone = Zone(raw_zone)
        except ValueError:
            listing = ", ".join(z.value for z in Zone)
            raise self._error(
                f"invalid zone type {raw_zone!r} (allowed: {listing})"
            ) from None
        return zone

    def _capacity(self, metadata: dict[str, str], key: str) -> int:
        """Read a capacity value from the metadata.

        Args:
            metadata: Parsed metadata.
            key: Name of the capacity key.

        Returns:
            The capacity, 1 by default.

        Raises:
            MapError: If the value is not a positive integer.
        """
        raw = metadata.get(key)
        if raw is None:
            return 1

        if not raw.isdecimal() or (val := int(raw)) == 0:
            raise self._error(f"{key} must be a positive integer got: {raw!r}")
        return val

    def _meta(
        self,
        bracket: str,
        metadata: str,
        keyword: str,
        allowed: frozenset[str],
    ) -> dict[str, str]:
        """Parse the `[key=value ...]` block of a line.

        Args:
            bracket: "[" if there is a metadata block, else empty.
            metadata: Text after the "[".
            keyword: Directive name, used in errors.
            allowed: Keys allowed for this directive.

        Returns:
            The metadata as a dict.

        Raises:
            MapError: If the block is malformed.
        """
        if not bracket:
            return {}
        if not allowed:
            raise self._error(f"directive {keyword!r} takes no metadata")
        metadata = metadata.strip()
        if not metadata.endswith("]"):
            raise self._error("unclosed metadata block: missing ']'")
        if "[" in metadata or "]" in metadata[:-1]:
            raise self._error("nested or repeated bracket in metadata block")

        listing = ", ".join(sorted(allowed))
        metadata_dict: dict[str, str] = {}
        for token in metadata.removesuffix("]").split():
            name, eq, value = token.partition("=")
            if not eq:
                raise self._error(
                    f"malformed metadata {token!r}: expected key=value"
                )
            if not name:
                raise self._error(f"malformed metadata {token!r}: empty key")
            if not value:
                raise self._error(f"metadata {name!r} has an empty value")
            if name in metadata_dict:
                raise self._error(f"duplicate metadata key {name!r}")
            if name not in allowed:
                raise self._error(
                    f"unknown metadata key {name!r}"
                    f"for {keyword!r} (allowed: {listing})"
                )
            metadata_dict[name] = value
        return metadata_dict

    def _coords(self, sx: str, sy: str) -> tuple[int, int]:
        """Convert the coordinates to integers.

        Args:
            sx: X as text.
            sy: Y as text.

        Returns:
            The (x, y) pair.

        Raises:
            MapError: If a value is not an integer.
        """
        try:
            return int(sx), int(sy)
        except ValueError:
            raise self._error(
                f"invalid coordinates, integers expected got: {sx!r}, {sy!r}"
            ) from None

    def _max_drones(self, hub_type: HubType, metadata: dict[str, str]) -> int:
        """Get the max drones of a hub.

        Args:
            hub_type: Kind of hub.
            metadata: Parsed metadata.

        Returns:
            The capacity, 0 (no limit) for start and end hubs.
        """
        if hub_type is not HubType.NORMAL:
            return 0
        return self._capacity(metadata, "max_drones")

    def _hub(
        self, hub_type: HubType, line_data: str, metadata: dict[str, str]
    ) -> Hub:
        """Parse a hub line.

        Args:
            hub_type: Kind of hub.
            line_data: Text after the ":" (name x y).
            metadata: Parsed metadata.

        Returns:
            The new hub.

        Raises:
            MapError: If the line is malformed.
        """
        keyword = hub_type.value
        fields = line_data.split()
        if len(fields) != 3:
            raise self._error(
                f"{keyword} expects 'name x y' got: {line_data!r}"
            )

        name, sx, sy = fields
        if "-" in name:
            raise self._error(f"{keyword} name cannot contain '-'")

        x, y = self._coords(sx, sy)
        return Hub(
            name=name,
            x=x,
            y=y,
            zone=self._get_zone(metadata),
            hub_type=hub_type,
            max_drones=self._max_drones(hub_type, metadata),
            color=metadata.get("color"),
        )

    def _link(self, line_data: str, metadata: dict[str, str]) -> Link:
        """Parse a connection line.

        Args:
            line_data: Text after the ":" (hub1-hub2).
            metadata: Parsed metadata.

        Returns:
            The new link.

        Raises:
            MapError: If the line is malformed.
        """
        from_hub, dash, to_hub = line_data.partition("-")

        if not dash or "-" in to_hub or " " in line_data:
            raise self._error(
                "connection expects exactly 'zone1-zone2' "
                f"(no spaces, one '-') got: {line_data!r}"
            )
        if not from_hub or not to_hub:
            raise self._error(f"connection missing a zone name: {line_data!r}")

        return Link(
            from_hub,
            to_hub,
            self._capacity(metadata, "max_link_capacity"),
        )

    def _nb_drones(self, line_data: str) -> int:
        """Parse the number of drones.

        Args:
            line_data: Text after the ":".

        Returns:
            The number of drones.

        Raises:
            MapError: If it is not a positive integer.
        """
        try:
            nb_drones = int(line_data)
        except ValueError:
            raise self._error(
                f"nb_drones invalid value got: {line_data!r} "
                "expected a positive integer"
            ) from None
        if nb_drones <= 0:
            raise self._error(f"nb_drones must be positive got: {nb_drones}")
        return nb_drones

    def parse(self) -> Hub | Link | int:
        """Parse the line.

        Returns:
            A Hub, a Link, or the number of drones.

        Raises:
            MapError: If the line is invalid.
        """
        name, _, data = self._text.partition(":")
        data, bracket, metadata = data.partition("[")

        if name not in ALLOWED.keys():
            raise self._error(
                f"prefix name is invalid expected: {','.join(ALLOWED.keys())} "
                f"got: {name}"
            )
        if not bracket and "]" in data:
            raise self._error("unmatched ']' with no opening '['")
        data = data.strip()
        metadata_dict = self._meta(bracket, metadata, name, ALLOWED[name])
        match name:
            case "nb_drones":
                return self._nb_drones(data)
            case "connection":
                return self._link(data, metadata_dict)
            case _:
                return self._hub(HubType(name), data, metadata_dict)
