(function() {
  var demo = {
    defaultOptions: {
      $container: $(".container-masonry"),
      $template: $("#item-template"),
      gutter: 20,
      imgWidth: 236,
      itemSelector: ".item",
      count: 20
    },

    options: {},

    items: [],

    init: function(options) {
      var self = this;
      self.options = $.extend({}, self.defaultOptions, options);
      self.getData(self.options.count, function() {
        var $container = self.options.$container;
        var html = self.generateHtml(self.options.$template, self.items);
        $container.append(html);
        self.startMasonry($container);
        self.loadImageMasonry($container);
      });
    },

    getData: function(count, callback) {
      for (var i = 0; i < count; i++) {
        var imageHeight = this.getRandomIntInclusive(10, 45) * 10;
        this.items.push({
          image:
            "https://unsplash.it/" +
            this.options.imgWidth +
            "/" +
            imageHeight +
            "/?random",
          title: faker.lorem.sentence(),
          source: faker.company.companyName(),
          pinCount: this.getRandomIntInclusive(1, 999),
          avatar: faker.image.avatar(),
          name: faker.name.findName(),
          tagline: faker.name.title()
        });
      }
      if (callback) callback();
    },

    generateHtml: function($selector, items) {
      var source = $selector.html();
      var template = Handlebars.compile(source);
      return template({ items: items });
    },

    startMasonry: function($container) {
      $container.masonry({
        itemSelector: this.options.itemSelector,
        columnWidth: this.options.itemWidth + this.options.gutter,
        fitWidth: true
      });
    },

    loadImageMasonry: function($container) {
      $container.imagesLoaded().progress(function() {
        $container.masonry("layout");
      });
    },

    getRandomIntInclusive: function(min, max) {
      min = Math.ceil(min);
      max = Math.floor(max);
      return Math.floor(Math.random() * (max - min + 1)) + min;
    }
  };

  demo.init();
})();
