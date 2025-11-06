window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        scrollToTop: function(input) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
            return window.dash_clientside.no_update;
        }
    }
});
