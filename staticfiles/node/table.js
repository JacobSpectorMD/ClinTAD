import {MDCSelect} from "@material/select";

export class Table {
    constructor(id, items, filter_field = null) {
        this.items = items;
        this.displayed_items = [...items];
        this.filtered_items = [...items];
        this.filter_field = filter_field;
        this.sorted_items = [];

        this.attributes = [];
        this.current_filter = {'attribute': null, 'term': ''};
        this.current_sort = {'attribute': null, 'order': 'default'};
        this.filtered = false;
        this.num_items = 10;
        this.start_num = 0;
        this.sorted = false;
        this.table_id = id;

        this.rows_select = this.get_rows_select();
        this.get_attributes();
        this.display_items();
        this.navigation_buttons();

    }

    display_items() {
        const table = this;
        table.remove_items();

        let slice_num = table.start_num + table.num_items;

        table.filter();
        table.sort();

        if (table.displayed_items.length < slice_num) {
            slice_num = table.displayed_items.length;
        }

        table.displayed_items.slice(table.start_num, slice_num).forEach(function (item) {
            add_item_to_table(table.table_id, table.attributes, item);
        })
        table.update_nav();
    }

    get_attributes() {
        const table = this;
        $('#' + table.table_id + ' .mdc-data-table__header-cell').each(function () {
            const header = this;
            const attribute = $(this).data('attribute');
            const sortable = $(this).data('sortable');

            if (sortable !== false) {
                $(header).append(`
                <i class="material-icons mdc-button__icon" aria-hidden="true">north</i>
              `)
            }

            // Sort by column when the arrows are clicked
            $(header).find('.material-icons').on('click', function () {
                table.add_sort(header, attribute);
            })

            // Add the column attribute to the filter input when the header text is clicked
            $(header).on('click', function (e) {
                if ($(e.target).hasClass('material-icons')) {
                    return
                }

                if (table.filter_field.value == attribute + ':') {
                    table.filter_field.value = ''
                } else {
                    table.filter_field.value = attribute + ':';
                }
            })

            // Add the attribute to the table
            table.attributes.push(attribute);
        })
    }

    get_rows_select() {
        const table = this;
        const select = document.querySelector('#' + table.table_id).closest('.mdc-data-table')
            .querySelector('.mdc-select');
        const mdcSelect = new MDCSelect(select);
        select.addEventListener('MDCSelect:change', function() {
            table.num_items = mdcSelect.value;
            table.display_items();
        })
        return mdcSelect;
    }

    add_filter(enteredTerm) {
        const table = this;
        let attribute = null;

        let filterTerm = '';
        if (enteredTerm.includes(':')) {
            attribute = enteredTerm.split(':')[0];
            filterTerm = enteredTerm.split(':')[1];
            if (filterTerm == '') {
                return
            }
        } else {
            filterTerm = enteredTerm;
        }

        table.current_filter.attribute = attribute;
        table.current_filter.term = filterTerm;

        table.display_items();
    }

    add_sort(header, attribute) {
        const table = this;
        $('#' + table.table_id).find('th .material-icons').html('north').css('opacity', '0.2');
        if (table.current_sort.attribute == attribute) {
            if (table.current_sort.order == 'ascending') {
                $(header).find('.material-icons').html('south').css('opacity', '1');
                table.current_sort.order = 'descending';
            } else if (table.current_sort.order == 'descending') {
                $(header).find('.material-icons').html('north').css('opacity', '0.2');
                table.current_sort.attribute = null;
                table.current_sort.order = 'default';
            } else if (table.current_sort.order == 'default') {
                $(header).find('.material-icons').css('opacity', '1');
                table.current_sort.order = 'ascending';
            }
        } else {
            $(header).find('.material-icons').css('opacity', '1');
            table.current_sort.attribute = attribute;
            table.current_sort.order = 'ascending';
        }

        table.display_items();
    }

    last_page_num() {
        // The number of the first item on the last page of the table
        if (this.displayed_items.length <= this.num_items) {
            return 0;
        }
        return Math.floor(this.items.length / this.num_items) * this.num_items - 1;
    }

    navigation_buttons() {
        const table = this;
        table.first_page_button = $(`#${table.table_id}`).closest('.mdc-data-table').find('button[data-first-page="true"]');
        table.previous_page_button = $(`#${table.table_id}`).closest('.mdc-data-table').find('button[data-prev-page="true"]');
        table.last_page_button = $(`#${table.table_id}`).closest('.mdc-data-table').find('button[data-last-page="true"]');
        table.next_page_button = $(`#${table.table_id}`).closest('.mdc-data-table').find('button[data-next-page="true"]');

        // First page button
        $(table.first_page_button).on('click', function () {
            table.start_num = 0;
            table.display_items();
        })

        // Last page button
        $(table.last_page_button).on('click', function () {
            table.start_num = table.last_page_num();
            table.display_items();
        })

        // Next page button
        $(table.next_page_button).on('click', function () {
            if (table.start_num + table.num_items > table.last_page_num()) {
                table.start_num = table.last_page_num();
            } else {
                table.start_num = table.start_num + table.num_items;
            }
            table.display_items();
        })

        // Previous page button
        $(table.previous_page_button).on('click', function () {
            if (table.start_num - table.num_items < 0) {
                table.start_num = 0;
            } else {
                table.start_num -= table.num_items;
            }
            table.display_items();
        })
    }

    remove_filter(attribute) {
        delete this.filters[attribute];
        if (Object.keys(this.filters).length == 0) {
            this.filtered = false;
        }
    }

    remove_items() {
        $('#' + this.table_id).find('tbody tr').remove();
    }

    filter() {
        const table = this;
        if (table.current_filter.term == '') {
            table.filtered_items = [...table.items];
            return;
        }

        if (table.current_filter.attribute) {
            table.filtered_items = [...table.items].filter(
                item => item[table.current_filter.attribute].toUpperCase().includes(table.current_filter.term.toUpperCase())
            );
        } else {
            table.filtered_items = [...table.items].filter(
                item => filter_all_attributes(table, item, table.current_filter.term)
            );
        }
    }

    sort() {
        const table = this;
        if (table.current_sort.order == 'default') {
            table.displayed_items = [...table.filtered_items];
            return
        }

        table.displayed_items = [...table.filtered_items].sort(function (a, b) {
            const attributeA = a[table.current_sort.attribute].toUpperCase();
            const attributeB = b[table.current_sort.attribute].toUpperCase();

            if (attributeA < attributeB) {
                return -1;
            }
            if (attributeA > attributeB) {
                return 1;
            }

            return 0;
        })

        if (table.current_sort.order == 'descending') {
            table.displayed_items.reverse();
        }
    }

    update_nav() {
        const table = this;
        $('#' + table.table_id).closest('.mdc-data-table').find('.start-num').html(table.start_num + 1);

        let end_num = parseInt(table.start_num + table.num_items);
        if (end_num > table.displayed_items.length) {
            end_num = table.displayed_items.length;
        }
        $('#' + table.table_id).closest('.mdc-data-table').find('.end-num').html(end_num);
        $('#' + table.table_id).closest('.mdc-data-table').find('.total-num').html(table.displayed_items.length);

        // Disable next page and last page button if on last page
        if (table.start_num == table.last_page_num() || table.start_num + table.num_items - 1 > table.displayed_items.length) {
            $(table.last_page_button).prop('disabled', true);
            $(table.next_page_button).prop('disabled', true);
        } else {
            $(table.last_page_button).prop('disabled', false);
            $(table.next_page_button).prop('disabled', false);
        }

        // Disable first page and previous page button if on first page
        if (table.start_num == 0) {
            $(table.first_page_button).prop('disabled', true);
            $(table.previous_page_button).prop('disabled', true);
        } else {
            $(table.first_page_button).prop('disabled', false);
            $(table.previous_page_button).prop('disabled', false);
        }
    }
}

function filter_all_attributes(table, item, filterTerm) {
    let attributes_string = '';
    table.attributes.forEach(function (attribute) {
        attributes_string += item[attribute];
    })
    return attributes_string.toLowerCase().includes(filterTerm.toLowerCase());
}

function add_item_to_table(table_id, attributes, item) {

    let row = $(`
        <tr class="mdc-data-table__row" data-id="${item.id}"></tr>
    `);

    attributes.forEach(function (attribute) {
        $(row).append(`
            <td class="mdc-data-table__cell">${item[attribute]}</td>
        `)
    });

    $(row).data('item', item);

    $('#' + table_id).append(row);
    item.row = row;
}