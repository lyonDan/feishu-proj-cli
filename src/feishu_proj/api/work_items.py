"""工作项读写 API"""


from feishu_proj.client import FeishuProjClient


def create_work_item(
    project_key: str,
    work_item_type_key: str,
    name: str,
    user_key: str | None = None,
    field_value_pairs: list | None = None,
    template_id: int | None = None,
) -> dict:
    client = FeishuProjClient(user_key=user_key)
    return client.create_work_item(
        project_key=project_key,
        work_item_type_key=work_item_type_key,
        name=name,
        field_value_pairs=field_value_pairs,
        template_id=template_id,
    )


def update_work_item(
    project_key: str,
    work_item_type_key: str,
    work_item_id: int,
    update_fields: list,
    user_key: str | None = None,
) -> dict:
    client = FeishuProjClient(user_key=user_key)
    return client.update_work_item(
        project_key=project_key,
        work_item_type_key=work_item_type_key,
        work_item_id=work_item_id,
        update_fields=update_fields,
    )


def get_work_item_meta(
    project_key: str,
    work_item_type_key: str,
    user_key: str | None = None,
) -> dict:
    client = FeishuProjClient(user_key=user_key)
    return client.get_work_item_meta(
        project_key=project_key,
        work_item_type_key=work_item_type_key,
    )


def delete_work_item(
    project_key: str,
    work_item_type_key: str,
    work_item_id: int,
    user_key: str | None = None,
) -> dict:
    client = FeishuProjClient(user_key=user_key)
    return client.delete_work_item(
        project_key=project_key,
        work_item_type_key=work_item_type_key,
        work_item_id=work_item_id,
    )
