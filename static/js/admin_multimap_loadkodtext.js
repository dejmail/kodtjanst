
if (window.document.location.hostname == "127.0.0.1") {
    var domain_url = '/';
    var domain_host = window.document.location.host
} else {
    var domain_url = "/"+window.location.pathname.split("/")[1]+"/";
    console.log("domain url" + domain_url);
    var domain_host = window.document.location.host
};    

window.onload = function() {

    // var x = document.getElementById('id_kodtext_from');
    // x.style.display = "block";

    if (window.jQuery) {  
        // jQuery is loaded  
        console.log("Yeah!");
    } else if (django.jQuery) {
        console.log('django available');
    } else {
        // jQuery is not loaded
        console.log("jQuery not available");
    }
};

window.addEventListener('load', function () {

    django.jQuery('#id_kodtext_from').hide();
    django.jQuery('#id_kodtext_to').hide();

    // replace what is in this field with the kodtext from the selected kodverk
    var is_kodverk_from_loaded = document.getElementById('id_kodverk_from');
    if(is_kodverk_from_loaded){
        is_kodverk_from_loaded.addEventListener('change', function() {
            console.log('Selected number ', this.value, ' kodverk');
            loadUrl(this.value, 'id_kodtext_from');

          });
    }

    // replace what is in this field with the kodtext from the selected kodverk
    var is_kodverk_to_loaded = document.getElementById('id_kodverk_to');
    if(is_kodverk_to_loaded){
        is_kodverk_to_loaded.addEventListener('change', function() {
            console.log('Selected number ', this.value, ' kodverk');
            loadUrl(this.value, 'id_kodtext_to');
          });
    }

    // Monitor which kodtexts are selected, place it in the JSON field
        django.jQuery('#id_kodtext_from', "#id_kodtext_to").change(function(e) {
            var selected = django.jQuery(e.target).val();
        }); 
    });


//  perform the ajax request for the kodtexts
function loadUrl(kodverk_id, kodtext_tag_id) {

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        django.jQuery('#'+kodtext_tag_id).empty().show();
        if (kodtext_tag_id.includes("to")) {
            django.jQuery("#multikodtextmapping_form > div > fieldset > div.form-row.field-kodtext_to > div > div").hide();
        } else {
            django.jQuery("#multikodtextmapping_form > div > fieldset > div.form-row.field-kodtext_from > div > div").hide();
        }
        document.getElementById(kodtext_tag_id).innerHTML = this.responseText;
        console.log('kodtext response loaded into form', kodtext_tag_id, 'field unhidden');
    }
    };
    
    var kodtext_url = domain_url+"admin/ajax/kodtext_elements/"+kodverk_id+"/"
    xhttp.open("GET", kodtext_url, true);
    xhttp.send();
};

function showhide_selection(div_to_toggle) {
    var x = document.getElementById(div_to_toggle);
    if (x.style.display === "none") {
      x.style.display = "block";
    } else {
      x.style.display = "none";
    }
  }
  