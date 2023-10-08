def picnic_table_to_list(picnic_table):
    result = []
    user_buffer = []
    prev_row = None
    rows_count = picnic_table.count()

    for idx, (picnic_id, time, user_id, city_name) in enumerate(picnic_table):
        # Если индекс пикника изменился
        if prev_row is not None:
            (prev_picnic_id, prev_time, prev_user_id, prev_city_name) = prev_row
            if picnic_id != prev_picnic_id:
                # Добавляем данные с предыдущим ИД пикника
                result.append(
                    {"id": prev_picnic_id, "city": prev_city_name, "time": prev_time, "users": user_buffer})
                user_buffer = []
        user_buffer.append(user_id)
        # Если это последняя строка
        if idx == rows_count - 1:
            print('is last row', (picnic_id, time, user_id, city_name))
            # Добавить запись в общий набор
            result.append({"id": picnic_id, "city": city_name, "time": time, "users": user_buffer})
        # Текущая строка становится предыдущей
        prev_row = (picnic_id, time, user_id, city_name)
