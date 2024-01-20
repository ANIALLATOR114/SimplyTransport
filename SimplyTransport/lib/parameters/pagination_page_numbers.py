def generate_pagination_pages(current_page: int, total_pages: int) -> list[int]:
    if total_pages <= 5:
        return list(range(1, total_pages + 1))
    else:
        # Generate the first page, last page, current page, and two pages around the current_page
        intermediate_pages = sorted(set([1, current_page - 1, current_page, current_page + 1, total_pages]))

        # Ensure the intermediate pages are within the valid page range
        intermediate_pages = [page for page in intermediate_pages if 1 <= page <= total_pages]

        # When at the start or end page, adds 2 more pages towards the middle
        if len(intermediate_pages) < 4:
            if current_page == 1:
                intermediate_pages.append(current_page + 2)
                intermediate_pages.append(current_page + 3)
            elif current_page == total_pages:
                intermediate_pages.append(current_page - 2)
                intermediate_pages.append(current_page - 3)

        # When at the second page or second last page, adds another page towards the middle
        if len(intermediate_pages) < 5:
            if current_page == 2:
                intermediate_pages.append(current_page + 2)
            elif current_page == total_pages - 1:
                intermediate_pages.append(current_page - 2)

        intermediate_pages = sorted(set(intermediate_pages))
        return intermediate_pages
