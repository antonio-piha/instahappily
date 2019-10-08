(function( $ ) {
  /**
   * List plugin jQuery
   */
  $.fn.list = function(options) {

    let $self = $(this);
    if ($self.length != 1) {
      throw "Must be called on one element."
    }

    let defaults = {
      on_add_item : ($item) => {},
      static_list: false,
      filter_by_input: true
    };

    let settings = $.extend( true, {}, defaults, options );

    let initiated = false;
    let list_items_count = 0;
    let $list_items = null;
    let $filter = null;
    let $metadata = null;
    let $template = null;
    let field_name = null;
    let last_index = null;

    //##################################################

    let init = () => {
      $list_items = $self.find('.js-list-items');
      $filter = $self.find('.js-list-filter');
      $metadata = $self.find('.js-list-metadata');
      $template = $self.find('.js-template').clone().eq(0);
      $items = $self.find('.js-list-item');
      list_items_count = $items.length;
      field_name = $metadata.data('fieldName');
      last_index = Number($metadata.data('lastIndex'));

      // After this point we can't continue if it was initated
      if (initiated) { return ;}

      toggle_js_list_filter();
      bind_events();
      initiated = true;
    }

    let remove_item = (remove_button) => {
      $(remove_button).parents('.js-list-item').remove();
      list_items_count--;
      toggle_js_list_filter();
    }

    let filter_list = () => {
      let filter = $(this).find('input').val();
      filter_lowercase = filter.toLowerCase();

      // Must be fetched here because of newly added elements
      // Slip if list is static, it will already have all items
      if (!settings.static_list) {
        $items = $self.find('.js-list-item');
      }

      $items.show();

      let filter_function = function () {
        if (settings.filter_by_input) {
          found = $( this ).val().toLowerCase().indexOf( filter_lowercase ) >= 0;
        } else {
          found = $( this ).text().toLowerCase().indexOf( filter_lowercase ) >= 0;
        }
        return found;
      }
      $items.each(function(i, item){
        $item = $(item)
        if (settings.filter_by_input) {
          $element_for_filtering = $item.find('input');
        } else {
          $element_for_filtering = $item;
        }

        if (!$element_for_filtering.filter(filter_function).length > 0) {
          $item.hide();
        }
      });

    }

    let get_template = () => {
      let template = $template.clone().children();
      template.find('input, select, textarea').attr('name', field_name + '-' + last_index);
      return template;
    }
    let update_last_index = () => {
      last_index++;
      $metadata.data('lastIndex', last_index);
    }

    let js_list_add_item = () => {
      update_last_index();
      let $item = get_template();
      $list_items.append($item);

      list_items_count++;
      toggle_js_list_filter();

      settings.on_add_item.call($item, $item);

      $item.find('input, textarea').focus();
    }

    let toggle_js_list_filter = () => {
      if (list_items_count > 10) {
        $filter.addClass('d-block');
      } else {
        $filter.removeClass('d-block');
      }
    }

    let bind_events = () => {
      $self
      .on('click', '.js-list-action-add', () => {
        js_list_add_item();
      })
      .on('click', '.js-list-action-remove', (event) => {
        remove_item(event.target);
      })
      .on('input', '.js-list-filter', () => {
        filter_list();
      })
      .on('keypress', '.js-list-item', (event) =>{
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if (keycode == 13 && !event.shiftKey) {
          js_list_add_item();
        }
      });
    }
    //##################################################

    init();

    return this;
  };



}( jQuery ));