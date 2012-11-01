/**
 * main.js - Javascript that must be ran on every page.
 * Author: Chris Manghane (paranoiacblack)
 */

$(document).ready(function() {
    // svgeezy.js is concantenated inside of plugin.js which is always
    // loaded before this.
    svgeezy.init('nocheck', 'png');

    // Multiple pages are using tooltips now so they should always be loaded.
    $("a[rel='tooltip']").tooltip();
});
