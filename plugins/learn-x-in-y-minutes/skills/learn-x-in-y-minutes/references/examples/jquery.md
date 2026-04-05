---
category: framework
name: jQuery
contributors:
    - ["Sawyer Charles", "https://github.com/xssc"]
filename: jquery.js
---

jQuery is a JavaScript library that helps you "do more, write less". It makes
many common JavaScript tasks easier. jQuery is used by many big companies and
developers everywhere for AJAX, event handling, and document manipulation.

```js
///////////////////////////////////
// 1. Selectors

// Selectors in jQuery are used to select an element
var page = $(window); // Selects the whole viewport

// Selectors can also be CSS selectors
var paragraph = $('p');          // Selects all paragraph elements
var table1 = $('#table1');       // Selects element with id 'table1'
var squares = $('.square');      // Selects all elements with the class 'square'
var square_p = $('p.square');    // Selects paragraphs with the 'square' class


///////////////////////////////////
// 2. Events and Effects

// Wait until the document is loaded before running code
$(document).ready(function(){
  // Code won't execute until the document is loaded
});

// Bind event handlers
$('#btn').click(onAction);       // Click
$('#btn').dblclick(onAction);    // Double click
$('#btn').hover(onAction);       // Hovering over
$('#btn').focus(onAction);       // On focus
$('#btn').blur(onAction);        // Loses focus
$('#btn').keydown(onAction);     // When a key is pushed down
$('#btn').keyup(onAction);       // When a key is released
$('#btn').mousemove(onAction);   // When the mouse is moved

// Show/hide elements with effects
var tables = $('.table');
tables.hide();                   // Hides element(s)
tables.show();                   // Shows (un-hides) element(s)
tables.toggle();                 // Changes the hide/show state
tables.fadeOut();                // Fades out
tables.fadeIn();                 // Fades in
tables.fadeToggle();             // Fades in or out
tables.fadeTo(0.5);              // Fades to an opacity (between 0 and 1)
tables.slideUp();                // Slides up
tables.slideDown();              // Slides down

// All effects take a speed (ms) and optional callback
tables.hide(1000, myFunction);   // 1 second hide animation then function


///////////////////////////////////
// 3. Manipulation

$('div').addClass('highlight');      // Adds class to all divs
$('p').append('Hello world');        // Adds to end of element
$('p').attr('class');                // Gets attribute
$('p').attr('class', 'content');     // Sets attribute
$('p').hasClass('highlight');        // Returns true if it has the class
$('p').height();                     // Gets height of first matching element
$('p').html();                       // Gets inner HTML
$('p').html('<b>new content</b>');   // Sets inner HTML
$('p').text();                       // Gets inner text (strips HTML)
$('p').text('new text');             // Sets inner text

// Loop through all matched elements
var heights = [];
$('p').each(function() {
  heights.push($(this).height());
});


///////////////////////////////////
// 4. AJAX

$.ajax({
  url: '/api/data',
  type: 'GET',          // or 'POST', 'PUT', 'DELETE', etc.
  data: { id: 1 },
  success: function(response) {
    console.log(response);
  },
  error: function(xhr) {
    console.error(xhr.status);
  }
});

// Shorthand GET
$.get('/api/data', { id: 1 }, function(response) {
  console.log(response);
});

// Shorthand POST
$.post('/api/submit', { name: 'Alice' }, function(response) {
  console.log(response);
});
```

<!-- Source: https://github.com/adambard/learnxinyminutes-docs/blob/master/jquery.md (truncated for reference) -->
