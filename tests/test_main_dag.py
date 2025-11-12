from dags.main_dag import get_cities_list


class TestGetCitiesList:
    def test_normal_case(self):
        """Тестируем нормальный случай с валидными данными"""

        test_records = (("Москва",), ("Санкт-Петербург",), ("Казань",))

        result = get_cities_list(test_records)

        assert result == ["Москва", "Санкт-Петербург", "Казань"]

    def test_empty_record(self):
        test_records = ()

        result = get_cities_list(test_records)

        assert result is None

    def test_none_records(self):
        """Тестируем None на входе"""
        # Arrange & Act
        result = get_cities_list(None)

        # Assert
        assert result is None

    def test_records_with_empty_tuples(self):
        """Тестируем список с пустыми кортежами"""
        # Arrange
        test_records = (("Москва",), (), ("Казань",), ())

        # Act
        result = get_cities_list(test_records)

        # Assert
        assert result == ["Москва", "Казань"]

    def test_records_with_none_elements(self):
        """Тестируем кортежи с None элементами"""
        # Arrange
        test_records = (("Москва",), (None,), ("Казань",), ("",))

        # Act
        result = get_cities_list(test_records)

        # Assert
        assert result == ["Москва", "Казань"]

    def test_records_with_empty_strings(self):
        """Тестируем кортежи с пустыми строками"""
        # Arrange
        test_records = (("Москва",), (" ",), ("Казань",), ("",))

        # Act
        result = get_cities_list(test_records)

        # Assert
        assert result == ["Москва", "Казань"]

    def test_mixed_valid_invalid_records(self):
        """Тестируем смесь валидных и невалидных записей"""
        # Arrange
        test_records = (
            ("Москва",),
            None,  # Сам кортеж None
            ("",),  # Пустая строка
            ("Санкт-Петербург",),
            (" ",),  # Пробел
            ("Казань",)
        )

        # Act
        result = get_cities_list(test_records)

        # Assert
        assert result == ["Москва", "Санкт-Петербург", "Казань"]

    def test_records_with_multiple_elements(self):
         """Тестируем кортежи с несколькими элементами (берем только первый)"""

         test_records = (("Москва", "Russia"), ("Сакнт-Петербург", "Russia"))

         result = get_cities_list(test_records)

         assert result == ["Москва", "Санкт-Петербург"]