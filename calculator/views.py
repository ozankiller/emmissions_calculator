from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
import numpy as np

from calculator.operations import (
    create_carbon_emmission,
    get_carbon_emmissions,
    get_emmission_factor,
    get_total_emmissions_sum,
    register_carbon_emmission_factor,
)
from calculator.types import TYPE_CONVERSIONS_DICT, Emmission, EmmissionFactor


@api_view(["POST"])
def register_emmission_factors(request):
    data = request.data
    filepath = data["filepath"]
    if not isinstance(filepath, str):
        return Response(
            {"message": "filepath is not valid string", "filepath": filepath},
            status=status.HTTP_400_BAD_REQUEST,
        )

    success = True
    try:
        df = pd.read_csv(filepath)
    except BaseException:
        return Response(
            {"message": "could not read csv from filepath", "filepath": filepath},
            status=status.HTTP_400_BAD_REQUEST,
        )
    df = df.fillna(np.nan).replace([np.nan], [None])
    for index, row in df.iterrows():
        emmission_factor = EmmissionFactor(
            activity=row["Activity"].lower(),
            lookup_identifier=row["Lookup identifiers"].lower(),
            unit=row["Unit"].lower(),
            co2e_factor=row["CO2e"],
            scope=row["Scope"],
            category=row["Category"],
        )
        success = success and register_carbon_emmission_factor(emmission_factor)

    return Response({"success": success})


@api_view(["POST"])
def read_emmission_records(request):
    data = request.data
    filepath = data["filepath"]
    if not isinstance(filepath, str):
        return Response(
            {"message": "filepath is not valid string", "filepath": filepath},
            status=status.HTTP_400_BAD_REQUEST,
        )

    success = True
    try:
        df = pd.read_csv(filepath)
    except BaseException:
        return Response(
            {"message": "could not read csv from filepath", "filepath": filepath},
            status=status.HTTP_400_BAD_REQUEST,
        )
    for index, row in df.iterrows():
        row_activity = row["Activity"].lower()
        if row_activity == "air travel":
            lookup_identifier = (
                row["Flight range"].lower() + ", " + row["Passenger class"].lower()
            )
            row_units = row["Distance units"].lower()
            row_value = row["Distance travelled"]

        elif row_activity == "electricity":
            lookup_identifier = row["Country"].lower()
            row_units = row["Units"].lower()
            row_value = row["Electricity Usage"]

        elif row_activity == "purchased goods and services":
            lookup_identifier = row["Supplier category"].lower()
            row_units = row["Spend units"].lower()
            row_value = row["Spend"]
        else:
            print(
                "Unknown Activity record received, activity : %s" % (row_activity,)
            )  # This would normally be a log
            success = False
            continue

        emmission_factor = get_emmission_factor(
            activity=row_activity, lookup_identifier=lookup_identifier
        )
        if emmission_factor is None:
            print(
                "Could not find emmission factor for activity : %s, lookup_identifier: %s"
                % (
                    row_activity,
                    lookup_identifier,
                )
            )  # This would normally be a log
            success = False
            continue
        if row_units != emmission_factor.unit:
            conversion_string = row_units + "-" + emmission_factor.unit
            if conversion_string not in TYPE_CONVERSIONS_DICT:
                print(
                    "Unknown unit received, cannot convert, unit : %s" % (row_units,)
                )  # This would normally be a log
                success = False
                continue
            final_value = TYPE_CONVERSIONS_DICT[conversion_string] * row_value
        else:
            final_value = row_value
        emmission_value = final_value * emmission_factor.co2e_factor

        emmission = Emmission(
            activity=row_activity,
            co2e=emmission_value,
            scope=emmission_factor.scope,
            category=emmission_factor.category,
        )
        success = success and create_carbon_emmission(emmission)

    return Response({"success": success})


@api_view(["POST"])
def get_emmissions(request):
    data = request.data
    is_sorted = data.get("is_sorted", None)
    filter_scope = data.get("filter_scope", None)
    filter_category = data.get("filter_category", None)
    grouped = data.get("grouped", None)

    if is_sorted is not None and not isinstance(is_sorted, bool):
        return Response(
            {"message": "is_sorted is not a valid boolean", "is_sorted": is_sorted},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if filter_scope is not None and not isinstance(filter_scope, int):
        return Response(
            {
                "message": "filter_scope is not a valid integer",
                "filter_scope": filter_scope,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if filter_category is not None and not isinstance(filter_category, int):
        return Response(
            {
                "message": "filter_category is not a valid integer",
                "filter_category": filter_category,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if grouped is None:
        grouped = False
    if not isinstance(grouped, bool):
        return Response(
            {"message": "grouped is not a valid boolean", "grouped": grouped},
            status=status.HTTP_400_BAD_REQUEST,
        )

    emmissions_list = get_carbon_emmissions(
        is_sorted=is_sorted,
        grouped=grouped,
        filter_category=filter_category,
        filter_scope=filter_scope,
    )

    emmissions_sum = get_total_emmissions_sum()

    return Response({"emmissions": emmissions_list, "emmissions_sum": emmissions_sum})
