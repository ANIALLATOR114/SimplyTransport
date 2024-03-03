from SimplyTransport.domain.maps.colors import Colors

def test_to_html_square():
    color = Colors.RED
    html_square = color.to_html_square()
    expected_html = '<span style="display: inline-block; width: 10px; height: 10px; background-color: red;"></span>'
    assert html_square == expected_html