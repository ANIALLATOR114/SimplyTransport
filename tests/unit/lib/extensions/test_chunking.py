import pytest
from SimplyTransport.lib.extensions.chunking import chunk_list


def test_chunk_list_with_even_chunks():
    # Arrange
    input_list = [1, 2, 3, 4, 6]
    chunk_size = 2

    # Act
    result = list(chunk_list(input_list, chunk_size))

    # Assert
    assert result == [[1, 2], [3, 4], [6]]


def test_chunk_list_with_empty_list():
    # Arrange
    input_list = []
    chunk_size = 2

    # Act
    result = list(chunk_list(input_list, chunk_size))

    # Assert
    assert result == []


def test_chunk_list_with_chunk_size_equal_to_list():
    # Arrange
    input_list = [1, 2, 3]
    chunk_size = 3

    # Act
    result = list(chunk_list(input_list, chunk_size))

    # Assert
    assert result == [[1, 2, 3]]


def test_chunk_list_with_invalid_chunk_size():
    # Arrange
    input_list = [1, 2, 3]

    # Act & Assert
    with pytest.raises(ValueError, match="Chunk size must be positive"):
        list(chunk_list(input_list, 0))


def test_chunk_list_preserves_type():
    # Arrange
    input_tuple = (1, 2, 3, 4, 5)
    chunk_size = 2

    # Act
    result = list(chunk_list(input_tuple, chunk_size))

    # Assert
    assert all(isinstance(chunk, tuple) for chunk in result)
    assert result == [(1, 2), (3, 4), (5,)]
