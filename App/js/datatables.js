(function(window, $) {

  let dynamic_datatable_options_defaults = {
    // properties
    columns: [
      {"data":"id"},
      {"data":"name"},
      {"data":"list_type"},
      {"data":"name_html"},
      {"data":"list_type_html"},
      {"data":"source"}
    ],
    select: true,
    // events
    on_select: (data) => {}
  }

  let settings = null;

  let initialized = 0;

  let init = (options) => {
    if (initialized) { return }
    initialized = 1;

    settings = $.extend( true, {}, dynamic_datatable_options_defaults, options );

    create_static_datatables();
    create_dynamic_datatables();

    post_init();
  }

  let post_init = () => {
    $('.dataTables_length').addClass('bs-select');
  }

  let create_static_datatables = () => {
    $('.js-data-table').dataTable();
  }

  let create_dynamic_datatables = () => {
    datatables = $('.js-data-table-select');
    datatables.dataTable(settings);

    datatables.on('select.dt', ( e, dt, type, indexes )=> {
      $datatable = $(e.target);
      let data = dt.rows(indexes).data();
      data = data && data.length > 0 ? data[0] : null;

      settings.on_select.call(null, data);
      $datatable.trigger('select.datatable', data);
    });

    datatables.on('deselect.dt', ( e, dt, type, indexes )=> {
      $datatable = $(e.target);
      $datatable.trigger('deselect.datatable');
    });
  }

  // OPTIMIZE: build tables by loading data from backend
  // let get_data_for_dynamic_tables = () => {
  //   $.getJSON('/api/get-custom-lists-sorted-by-list-type')
  //     .done(function(data) {
  //       create_dynamic_datatables(data);
  //     })
  //     .fail(function() {
  //     })
  //     .always(function() {
  //     });
  // }

  window.wDataTables = {
    init: init
  };
}(window, jQuery));