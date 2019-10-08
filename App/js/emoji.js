(function(window, $) {
  let Emoji = class {
    constructor() {
      // Private
      // Targets should be inputs
      this.input_to_enable_selector = '[data-emojiable-for-enable]';
      this.editor_selector = '.emoji-wysiwyg-editor';
      this.element_attributes = {
        'data-emojiable' : 'true',
        'data-emoji-input' : 'unicode'
      };
      this.emoji_picker = new EmojiPicker({
        emojiable_selector: '[data-emojiable=true]',
        assetsPath : '/static/img',
        popupButtonClasses: 'far fa-smile'
      });

      // Public
      this.on_discover = () => {};
    }

    discover(root) {
      let $root = root ? $(root) : null;
      let $input_elements = null;
      if ($root) {
        $input_elements = $root.find(this.input_to_enable_selector);
      } else {
        $input_elements = $(this.input_to_enable_selector);
      }

      $input_elements.attr(this.element_attributes);

      this.emoji_picker.discover();

      this._fix_editors($input_elements);
    }

    _fix_editors($input_elements) {
      // To trigger adding .parent-has-scroll class defined in emoji/emojiarea plugin
      $input_elements.siblings(this.editor_selector).scroll();
    }
  }

  window.wEmoji = Emoji;
}(window, jQuery));