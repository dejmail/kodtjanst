const user_input = $("#user-input");
const search_icon = $('#search-icon');
const target_div = $('#mitten-span-middle-column');
var currentPage = window.document.domain;

function endpoint_check() {

    if (document.domain == "127.0.0.1") { 
		const endpoint = '/';
		return endpoint
    } else {
		const endpoint = document.URL;
		return endpoint
	}

}

function toggle_element(element_id, status) {
    var x = document.getElementById(element_id);
    x.style.display = status;
    }

const endpoint = endpoint_check();

function search_ajax_call(endpoint, request_parameters, skapad_url) {

		changeBrowserURL('', endpoint_check());
		$("#term_förklaring_tabell").remove();
		$("#mitten-span-middle-column").empty();
		if(typeof skapad_url !== 'undefined'){
			var skapad_url = (endpoint + skapad_url);
		} else {
			var skapad_url = (endpoint + '?q=' + request_parameters);
		}
		console.log('skapad_url is', skapad_url)

		$.ajax({
			type: "GET",
			dataType: "html",
			url: skapad_url,
		}).done(function(data, textStatus, jqXHR) {
			$("#mitten-span-middle-column").empty();
			//var data = data.replace('\n','').replace('  ', '').replace(/[\r\n]/gm, '');
			document.getElementById('user-input').value = '';
			clean_data = JSON.parse(data).payload.replaceAll('\n','');
			$('#mitten-span-middle-column').html(clean_data);
			
			changeBrowserURL(response.payload, skapad_url);
			// fade out the target_div, then:
			target_div.fadeTo('fast', 0).promise().then(() => {
				// replace the HTML contents
				target_div.html(response.payload);
				// fade-in the div with new contents
				target_div.fadeTo('fast', 1);
				// stop animating search icon
				search_icon.removeClass('blink');
				popStateHandler();
			})
		})
		.fail(function(data,textStatus,jqXHR) {        
			  $('#mitten-span-middle-column').html("Fel - Hoppsan! Jag får ingen definition från servern...finns ett problem..prova trycka Ctrl-Shift-R");
			});
		};

		  
		// $.getJSON(endpoint, request_parameters)
		// 	.done(response => {
		// 		console.log("document.URL", document.URL)
		//         console.log("endpoint", endpoint);
		// 		changeBrowserURL(response.payload, skapad_url);
		// 		// fade out the target_div, then:
		// 		target_div.fadeTo('fast', 0).promise().then(() => {
		// 			// replace the HTML contents
		// 			target_div.html(response.payload);
		// 			// fade-in the div with new contents
		// 			target_div.fadeTo('fast', 1);
		// 			// stop animating search icon
		// 			search_icon.removeClass('blink');
		// 			popStateHandler();
		// 		})
		// 	});
		// popStateHandler();
	// }

function debounce( callback, delay ) {
		let timeout;
		return function() {
			clearTimeout( timeout );
			timeout = setTimeout( callback, delay );
		}
	}

const searchInput = document.getElementById("user-input");

//user_input.keyup(function () {
function send_search() {
	
	$("#mitten-span-middle-column").empty();
	toggle_element("helpInfo", "none");
	// start animating the search icon with the CSS class
	search_icon.addClass('blink')
		
	if (searchInput.value.length > 1) {
		var ajax_call = search_ajax_call(
			endpoint,
			searchInput.value
		);
	} 
	
	};

document.getElementById("user-input").addEventListener(
		"keyup",
		debounce(send_search, 500 )
	);

document.body.addEventListener("click", function(e) {
	// e.target was the clicked element
	if(e.target && e.target.nodeName == "A") {

		if (e.target.hostname == currentPage) {	
			// catch only internal A clicks, allow external links to proceed
			// Stop the browser redirecting to  the HREF value.
			e.preventDefault();    
			console.log("sending", e.target.id, "ID to URL", e.target.href);
			// Attach event listeners for browser history and hash changes.
		
			//changeBrowserURL(null, e.target.href);            
			// Get page and replace current content.
			//debugger;
			getPage(e.target.href);
			popStateHandler();
		}
	}
});

function getPage(link_url) {

	console.log('entering ajax getPage function');
	$.ajax({
		type: "GET",
		dataType: "html",
		url: link_url,
	}).done(function(data, textStatus, jqXHR) {
		$("#mitten-span-middle-column").empty();
		//var data = data.replace('\n','').replace('  ', '').replace(/[\r\n]/gm, '');
		document.getElementById('user-input').value = '';
		clean_data = JSON.parse(data).payload.replaceAll('\n','');
		$('#mitten-span-middle-column').html(clean_data);
		changeBrowserURL(clean_data, this.url);
	}).fail(function(data,textStatus,jqXHR) {        
		  $('#mitten-span-middle-column').html("Fel - Hoppsan! Jag får ingen definition från servern...finns ett problem..prova trycka Ctrl-Shift-R");
		});
	  };

/*
* Function to modify URL within browser address bar.
*/

function changeBrowserURL(data, href) {
	// Change URL with browser address bar using the HTML5 History API.
	if (history.pushState) {
	  console.log('in changeBrowserURL function, changing URL to', href)
	  // Parameters: data, page title, URL
	  history.pushState(data, null, href);
	}
	
   };

/*
 * Function to detect when back and forward buttons clicked.
 *
 * This function will allow us to load content on the fly, as
 * the browser cannot re-render the AJAX content between state changes.
 */
function popStateHandler() {
	// FF, Chrome, Safari, IE9.
	if (history.pushState) {
	  // Event listener to capture when user pressing the back and forward buttons within the browser.
	  console.log('popStateHandler  - history.pushState variable exists');
	  window.addEventListener("popstate", function(e) {
		// Get the URL from the address bar and fetch the page.
		console.log('popstateHandler eventlistener fired, next stop getPage function')
		//debugger;
		$('#mitten-span-middle-column').html(history.state);
		//getPage(document.URL);
	  });
}
};

$(document).ready(function(){
	$('[data-toggle="popover_nyakodverk"]').popover({
		 //trigger: 'focus',
		 trigger: 'hover',
		 html: true,
		 content: function () {
			   return '<div class="media"><div class="media-body"><p>Nya kodverk publicerade av VGR IoS. Kopiera länkadressen från ikonen genom att högerklicka, kopiera och sedan klistra in i RSS program t.ex Outlook</p></div></div>';
		 },
   }) 
});

$(document).ready(function(){
	$('[data-toggle="popover_ändringar"]').popover({
		 //trigger: 'focus',
		 trigger: 'hover',
		 html: true,
		 content: function () {
			   return '<div class="media"><div class="media-body"><p>Förändringar som har skett i kodverk från VGR IoS. Kopiera länkadressen från ikonen genom att högerklicka, kopiera och klistra in i RSS program t.ex Outlook</p></div></div>';
		 },
   }) 
});