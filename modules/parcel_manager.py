"""
modules/parcel_manager.py
--------------------------
Provides the ParcelManager class for managing Parcel records.

A Parcel is a plain dict with the following keys:
    id          : str  — unique identifier, e.g. "P001"
    name        : str  — descriptive parcel name
    weight      : float — weight in kilograms
    priority    : int  — urgency level 1–5 (5 = most urgent)
    deadline    : str  — delivery deadline "YYYY-MM-DD"
    destination : str  — delivery location name
    value       : float — computed as priority * 10
"""

import csv
import os
from typing import Any, Dict, List, Optional

from algorithms.sorting import (
    sort_by_combined,
    sort_by_deadline,
    sort_by_priority,
)


class ParcelManager:
    """
    Manages a collection of Parcel dicts.

    Attributes
    ----------
    parcels : list[dict]
        In-memory list of all parcel records.
    """

    def __init__(self) -> None:
        self.parcels: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _next_id(self) -> str:
        """Generate the next sequential parcel ID (P001, P002, …)."""
        existing_nums = []
        for p in self.parcels:
            pid = p.get("id", "")
            if pid.startswith("P") and pid[1:].isdigit():
                existing_nums.append(int(pid[1:]))
        next_num = max(existing_nums, default=0) + 1
        return f"P{next_num:03d}"

    @staticmethod
    def _make_parcel(
        pid: str,
        name: str,
        weight: float,
        priority: int,
        deadline: str,
        destination: str,
    ) -> Dict[str, Any]:
        """Create a Parcel dict from individual fields."""
        return {
            "id": pid,
            "name": str(name),
            "weight": float(weight),
            "priority": int(priority),
            "deadline": str(deadline),
            "destination": str(destination),
            "value": float(int(priority) * 10),
        }

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def add_parcel(
        self,
        name: str,
        weight: float,
        priority: int,
        deadline: str,
        destination: str,
    ) -> Dict[str, Any]:
        """
        Add a new parcel to the collection.

        Parameters
        ----------
        name        : parcel description / label
        weight      : weight in kg
        priority    : integer 1–5
        deadline    : "YYYY-MM-DD" string
        destination : delivery location name

        Returns
        -------
        The newly created Parcel dict (with auto-generated id).
        """
        parcel = self._make_parcel(
            pid=self._next_id(),
            name=name,
            weight=weight,
            priority=priority,
            deadline=deadline,
            destination=destination,
        )
        self.parcels.append(parcel)
        return parcel

    def delete_parcel(self, parcel_id: str) -> bool:
        """
        Remove the parcel with the given id.

        Returns True if found and removed, False if id not found.
        """
        original_len = len(self.parcels)
        self.parcels = [p for p in self.parcels if p["id"] != parcel_id]
        return len(self.parcels) < original_len

    def edit_parcel(self, parcel_id: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """
        Update fields on an existing parcel.

        Allowed field names: name, weight, priority, deadline, destination.
        'id' cannot be changed. 'value' is recomputed if 'priority' changes.

        Returns the updated Parcel dict, or None if parcel_id not found.
        """
        parcel = self.get_parcel_by_id(parcel_id)
        if parcel is None:
            return None

        allowed = {"name", "weight", "priority", "deadline", "destination"}
        for key, val in kwargs.items():
            if key in allowed:
                parcel[key] = val

        # Recompute value whenever priority changes
        parcel["value"] = float(int(parcel["priority"]) * 10)
        # Ensure types
        parcel["weight"] = float(parcel["weight"])
        parcel["priority"] = int(parcel["priority"])
        return parcel

    def get_all_parcels(self) -> List[Dict[str, Any]]:
        """Return a copy of the full parcel list."""
        return list(self.parcels)

    def get_parcel_by_id(self, parcel_id: str) -> Optional[Dict[str, Any]]:
        """Return the Parcel dict with the given id, or None if not found."""
        for p in self.parcels:
            if p["id"] == parcel_id:
                return p
        return None

    # ------------------------------------------------------------------
    # CSV I/O
    # ------------------------------------------------------------------

    _CSV_FIELDS = ["id", "name", "weight", "priority", "deadline", "destination", "value"]

    def load_from_csv(self, filepath: str) -> None:
        """
        Replace self.parcels with parcels loaded from a CSV file.

        Expected columns: id, name, weight, priority, deadline, destination, value
        """
        parcels: List[Dict[str, Any]] = []
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                parcel = {
                    "id": row["id"].strip(),
                    "name": row["name"].strip(),
                    "weight": float(row["weight"]),
                    "priority": int(row["priority"]),
                    "deadline": row["deadline"].strip(),
                    "destination": row["destination"].strip(),
                    "value": float(row["value"]),
                }
                parcels.append(parcel)
        self.parcels = parcels

    def save_to_csv(self, filepath: str) -> None:
        """
        Save the current parcels list to a CSV file.

        Creates parent directories if they do not exist.
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self._CSV_FIELDS)
            writer.writeheader()
            for p in self.parcels:
                writer.writerow({k: p[k] for k in self._CSV_FIELDS})

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def sort_parcels(self, by: str = "combined") -> List[Dict[str, Any]]:
        """
        Return a sorted copy of self.parcels (original list not mutated).

        Parameters
        ----------
        by : one of "priority", "deadline", "combined" (default)
             "combined" → primary: priority desc, secondary: deadline asc

        Returns
        -------
        Sorted list of Parcel dicts.
        """
        by = by.lower().strip()
        if by == "priority":
            return sort_by_priority(self.parcels)
        elif by == "deadline":
            return sort_by_deadline(self.parcels)
        else:
            return sort_by_combined(self.parcels)
