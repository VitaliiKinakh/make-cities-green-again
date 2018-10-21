let list = data.map(function(i) { 
    if (i && i.name)
        return i["name"].toString(); }
);
let test = new Awesomplete(document.getElementById("cityField"))
test.filter = function (text, input) {
	return text.toLowerCase().startsWith(input.toLowerCase());
}
test.list = list;

$('form').submit(function(e){
    let city = $('input').val().toUpperCase();
    if (list.indexOf(city)!==-1) window.location.replace("/map/"+city.toLowerCase());
    e.preventDefault();
})