/* Remove open css class from all navigation option */
function removeNavOpenState() {
    $('.dropdown dropdown-fw active selected').each(function(index, elem) {
        $(elem).removeClass("open");
    });
}

/* Set open css class on specific navigation option and disable its anchor link */
function setNavOpenStateOn(jQElem) {
    jQElem.addClass("open");
    jQElem.find('a:first').attr('href', 'javascript:;');
}
