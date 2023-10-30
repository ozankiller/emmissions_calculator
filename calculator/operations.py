from typing import List, Optional, Union
from django.db.models import Sum
from calculator import models
from calculator.types import ClientEmmission, Emmission, EmmissionFactor, GroupedEmmission


def register_carbon_emmission_factor(emmission_factor: EmmissionFactor) -> bool:
    # Function to register carbon emmission factor in database, returns True if successful, False otherwise.
    try:
        models.EmmissionFactor.objects.create(
            activity=emmission_factor.activity,
            lookup_identifier=emmission_factor.lookup_identifier,
            unit=emmission_factor.unit,
            co2e_factor=emmission_factor.co2e_factor,
            scope=emmission_factor.scope,
            category=emmission_factor.category,
        )

    except BaseException:
        print(
            "Failed to register new carbon emmission factor, activity: %s, lookup_identifier: %s"
            % (
                emmission_factor.activity,
                emmission_factor.lookup_identifier,
            )
        )  # This would normally be a log
        return False

    return True


def get_emmission_factor(
    activity: str, lookup_identifier: str
) -> Optional[EmmissionFactor]:
    # Function to get carbon emmission factor from database, depending on activity and lookup identifier, returns None if none found
    emmission_factor = models.EmmissionFactor.objects.filter(
        activity=activity, lookup_identifier=lookup_identifier
    ).first()

    if emmission_factor is not None:
        return convert_db_emmission_factor(emmission_factor)
    return None


def create_carbon_emmission(emmission: Emmission) -> bool:
    # Function to create new carbon emmission in database, returns True if successful, False otherwise.
    try:
        models.Emmission.objects.create(
            activity=emmission.activity,
            co2e=emmission.co2e,
            scope=emmission.scope,
            category=emmission.category,
        )

    except BaseException:
        print(
            "Failed to register new carbon emmission, activity: %s, co2e: %s"
            % (
                emmission.activity,
                emmission.co2e,
            )
        )  # This would normally be a log
        return False

    return True


def get_carbon_emmissions(
    is_sorted: Optional[bool] = None,
    grouped: bool = False,
    filter_scope: Optional[int] = None,
    filter_category: Optional[int] = None,
) -> List[Union[ClientEmmission, GroupedEmmission]]:
    # Function to get carbon emmission data and sort it, filter it and aggregate it by activity type if necessary
    # For is_sorted parameter, if None we do not sort, if True we sort in descending order, if False we sort in ascending order
    emmissions = models.Emmission.objects
    if filter_scope is not None:
        emmissions = emmissions.filter(scope=filter_scope)
    if filter_category is not None:
        emmissions = emmissions.filter(category=filter_category)
    if is_sorted is not None:
        if is_sorted:
            emmissions = emmissions.order_by("-co2e")
        else:
            emmissions = emmissions.order_by("co2e")

    final_emmissions_list = list(emmissions.all())

    if grouped:
        emmissions_activity_dict = {}
        for emmission in final_emmissions_list:
            if emmission.activity not in emmissions_activity_dict:
                emmissions_activity_dict[emmission.activity] = GroupedEmmission(
                    activity=emmission.activity,
                    count=0,
                    total_co2e=0,
                    category=emmission.category,
                    scope=emmission.scope,
                )
            emmissions_activity_dict[emmission.activity]["count"] += 1
            emmissions_activity_dict[emmission.activity]["total_co2e"] += emmission.co2e

        if is_sorted is not None:
            grouped_values = sorted(
                emmissions_activity_dict.values(),
                reverse=is_sorted,
                key=lambda activity: activity["total_co2e"],
            )
        else:
            grouped_values = emmissions_activity_dict.values()

        return list(grouped_values)

    return [
        convert_db_emmission_to_client_dict(db_emmission) for db_emmission in final_emmissions_list
    ]


def get_total_emmissions_sum() -> float:
    # function to get total emmissions sum
    return models.Emmission.objects.aggregate(Sum("co2e"))["co2e__sum"]


def convert_db_emmission_factor(
    db_emmission_factor: models.EmmissionFactor,
) -> EmmissionFactor:
    return EmmissionFactor(
        activity=db_emmission_factor.activity,
        lookup_identifier=db_emmission_factor.lookup_identifier,
        unit=db_emmission_factor.unit,
        co2e_factor=db_emmission_factor.co2e_factor,
        scope=db_emmission_factor.scope,
        category=db_emmission_factor.category,
    )


def convert_db_emmission_to_client_dict(db_emmission: models.Emmission) -> ClientEmmission:
    return ClientEmmission(
        activity=db_emmission.activity,
        co2e=db_emmission.co2e,
        scope=db_emmission.scope,
        category=db_emmission.category,
    )
