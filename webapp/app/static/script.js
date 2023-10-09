/* Cart Variables */

var selectedServicesIndexes = new Array();
var selectedDateIsoformat = null;
var selectedTimeIsoformat = null;


/* Telegram Variables */

var WebApp = window.Telegram.WebApp;
var MainButton = WebApp.MainButton;
var BackButton = WebApp.BackButton;
MainButton.hide();
BackButton.hide();
MainButton.setText("SELECT DATE AND TIME");


/* Sections */

var currentSection = 'select_services';

function loadSelectServices() {
	MainButton.setText("SELECT DATE AND TIME");
	$('#select_date_and_time').hide();
	$('#select_services').show();
	currentSection = 'select_services';
}

function loadSelectDateAndTime() {
	MainButton.setText("BOOK");
	$('#select_services').hide();
	$('#select_date_and_time-times').hide();
	loadDates();
	$('#select_date_and_time').show();
	currentSection = 'select_date_and_time';
}


/* select_services */

$('.select_service').click(function() {
	const serviceIndex = parseInt($(this).attr('data-service_index'));
	if (!selectedServicesIndexes.includes(serviceIndex)) {
		$(this).addClass('select_service-selected');
		selectedServicesIndexes.push(serviceIndex);
	} else {
		$(this).removeClass('select_service-selected');
		selectedServicesIndexes.splice(selectedServicesIndexes.indexOf(serviceIndex), 1);
	}

	if (selectedServicesIndexes.length > 0) {
		if (!MainButton.isVisible) {
			MainButton.show();
		}
	} else {
		if (MainButton.isVisible) {
			MainButton.hide();
		}
	}
});


/* select_date_and_time */

let months = [
	"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
]

function stylizeTime(timeIsoformat) {
	return timeIsoformat.slice(0, 5);
}

function stylizeDate(dateIsoformat) {
	let monthInt = parseInt(dateIsoformat.slice(5, 6 + 1));
	let day = parseInt(dateIsoformat.slice(8, 9 + 1));

	let today = new Date();
	if (today.toISOString().slice(0, 9 + 1) == dateIsoformat) {
		return "today";
	} else {
		today.setDate(today.getDate() + 1);
		if (today.toISOString().slice(0, 9 + 1) == dateIsoformat) {
			return "tomorrow";
		} else {
			return `${months[monthInt - 1]}, ${day}`;
		}
	}
}


function loadDates() {
	$('#select_date_and_time-dates').empty();
	selectedDateIsoformat = null;

	for (let dateIsoformat in window.freeDates) {
		let div = document.createElement('div');
		div.classList.add('select_date');
		div.setAttribute('data-date_iso', dateIsoformat);
		div.onclick = function() {
			if (selectedDateIsoformat != null) {
				$(`.select_date[data-date_iso='${selectedDateIsoformat}']`).removeClass('select_date-selected');
			}
			$(this).addClass('select_date-selected');
			selectedDateIsoformat = dateIsoformat;
			loadTimes(dateIsoformat);
		};
		div.textContent = stylizeDate(dateIsoformat);

		$('#select_date_and_time-dates').append(div);
	}
}

function loadTimes(selectedDateIsoformat) {
	$('#select_date_and_time-times').empty();
	selectedTimeIsoformat = null;

	for (let i in window.freeDates[selectedDateIsoformat]) {
		let timeIsoformat = window.freeDates[selectedDateIsoformat][i];

		let div = document.createElement('div');
		div.classList.add('select_time');
		div.setAttribute('data-time_iso', timeIsoformat)
		div.onclick = function() {
			if (selectedTimeIsoformat != null) {
				$(`.select_time[data-time_iso='${selectedTimeIsoformat}']`).removeClass('select_time-selected');
			}
			$(this).addClass('select_time-selected');
			selectedTimeIsoformat = timeIsoformat;
		};
		div.textContent = stylizeTime(timeIsoformat);

		$('#select_date_and_time-times').append(div);
	}

	$('#select_date_and_time-times').show();
}


/* Telegram Functions */

MainButton.onClick(function() {
	if (currentSection == 'select_services') {
		loadSelectDateAndTime();
		if (!BackButton.isVisible) {
			BackButton.show();
		}
	} else if (currentSection == 'select_date_and_time') {

		if (!selectedDateIsoformat || !selectedTimeIsoformat) {
			WebApp.showAlert("Please select a date and time for the appointment");
			return null;
		}

		let selectedServicesIds = new Array();
		let prices = new Array();
		for (let selectedServiceIndex of selectedServicesIndexes) {
			selectedServicesIds.push(window.services[selectedServiceIndex].pk);
			prices.push({
				'label': window.services[selectedServiceIndex].fields.title,
				'amount': window.services[selectedServiceIndex].fields.price * 100
			})
		}

		let requestParams = {
			'description': `Beauty salon services for you on ${stylizeDate(selectedDateIsoformat)} at ${stylizeTime(selectedTimeIsoformat)}`,
			'prices': JSON.stringify(prices),
			'payload': `${window.userId} ${window.initMessageId} ${JSON.stringify(selectedServicesIds)} ${selectedDateIsoformat} ${selectedTimeIsoformat}`,

			'initDataHash': initDataHash,
			'dataCheckString': dataCheckString,
		}

		let requestURL = new URL(`${window.location.origin}/bot/create_invoice_link`);
		requestURL.searchParams.set('description', requestParams['description']);
		requestURL.searchParams.set('prices', requestParams['prices']);
		requestURL.searchParams.set('payload', requestParams['payload']);
		requestURL.searchParams.set('initDataHash', requestParams['initDataHash']);
		requestURL.searchParams.set('dataCheckString', requestParams['dataCheckString']);

		let xhr = new XMLHttpRequest();
		xhr.open('GET', requestURL);
		xhr.send();
		xhr.onload = function() {
			window.Telegram.WebApp.openInvoice(JSON.parse(xhr.response).result);
		}
	}
});

BackButton.onClick(function() {
	if (currentSection == 'select_date_and_time') {
		loadSelectServices();
		if (BackButton.isVisible) {
			BackButton.hide();
		}
	}
});

window.Telegram.WebApp.onEvent('invoiceClosed', function(object) {
	if (object.status == 'pending' || object.status == 'paid') {
		window.Telegram.WebApp.close();
	}
});
