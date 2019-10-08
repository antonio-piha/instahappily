(function( $ ) {

  $.fn.custom_list_picker = function(options) {

    let $self = $(this);
    if ($self.length != 1) {
      throw "Must be called on one element."
    }

    let defaults = {};
    let settings = $.extend( true, {}, defaults, options );

    let initiated = false;

    let list_type_key = null;
    let $modal = null;
    let $open_button = null;
    let $remove_button = null;
    let $field = null;
    let $field_input = null;
    let field_initial_value = null;
    let $field_info = null;
    let $field_info_name = null;

    //##################################################

    let init = () => {
      list_type_key = $self.data('listTypeKey');
      $modal = $('.js-custom-list-picker-modal[data-list-type-key="' + list_type_key + '"]');
      $open_button = $self.find('.js-custom-list-open-picker');
      $remove_button = $self.find('.js-custom-list-remove');
      // Field - hidden input
      $field = $self.find('.js-custom-list-field').find('.js-object-field');
      $field_input = $field.find('input');
      field_initial_value = $field.find('.js-initial-value').text();
      // Field info - display the field values
      $field_info = $self.find('.js-custom-list-field-info');
      $field_info_name =  $field_info.find('.js-custom-list-field-info-name');


      // After this point we can't continue if it was initiated
      if (initiated) { return ;}

      initiated = true;

      $modal.modal({
        show: false
      });

      $open_button.on('click', open_picker);
      $remove_button.on('click', remove)

      set_field_data_on_init();
    }

    let open_picker = () => {
      $modal.modal('show');
      // These handlers must be added here becuase we are using same modals for several openers

      // Event listeners for datables from inside modals
      $modal.on('select.datatable', (e, data) => {
        set_field_data(data);
      });
      $modal.on('deselect.datatable', unset_field_data);

      $modal.on('hide.bs.modal', () => {
        // Important, remove event handler
        $modal.off('select.datatable');
        $modal.off('deselect.datatable');
      });
    }

    let remove = () => {
      unset_field_data();
      $remove_button.addClass('d-none');
    }

    let set_field_data = (data) => {
      // Store only values
      let value = {
        id: data.id,
        name: data.name,
        list_type: data.list_type,
        source: data.source
      }
      value = JSON.stringify(value);

      $field_input.val(value);
      $field_info.removeClass('d-none');
      $field_info_name.html(
        'Using ' + '<div class="d-inline-block">' + data.source + '</div>: ' + data.name
      );

      $remove_button.removeClass('d-none');
    }

    let unset_field_data = (e) => {
      $field_input.val('');
      $field_info.addClass('d-none');
      $field_info_name.html('');
    }

    let set_field_data_on_init = () => {
      if (field_initial_value === '') return;
      let data = null;
      try {
        data = JSON.parse(field_initial_value);
      } catch(error) {
        console.log(error);
        data = null;
      }
      if (data) {
        set_field_data(data);
      }
    }
    //##################################################

    init();

    return this;
  };

}( jQuery ));



(function(window, $) {
  let init = () => {
    custom_lists_forms();
    custom_lists_pickers();
  }

  let custom_lists_forms = () => {
    $custom_list_wrapper = $('.js-custom-list-form-wrap');
    if ($custom_list_wrapper.length == 0) { return }

    let $custom_list_fields = {'usernames': null, 'hashtags': null, 'comments': null, 'locations': null, 'links': null};
    Object.keys($custom_list_fields).forEach((key) => {
      $custom_list_fields[key] = $custom_list_wrapper.find('.js-custom-list-' + key);
    });
    $custom_list_holder = $custom_list_wrapper.find('.js-custom-list-holder');
    $custom_list_storage = $custom_list_wrapper.find('.js-custom-list-storage');
    // $custom_list_type_key listener
    $custom_list_type = $custom_list_wrapper.find('.js-custom-list-type-key').find('select');
    let custom_list_type_change = function () {
      type_key = $custom_list_type.val();
      if (!type_key) return;
      // Swap
      current_list = $custom_list_holder.children().appendTo($custom_list_storage);
      $custom_list_fields[type_key].appendTo($custom_list_holder);
    }
    custom_list_type_change();
    $custom_list_type.on('change', custom_list_type_change);
  }

  let custom_lists_pickers = () => {
    $('.js-custom-list-picker').each(function (i, element) {
      $(element).custom_list_picker();
    });
  }

  window.wCustomLists = {
    init : init
  }
}(window, jQuery));