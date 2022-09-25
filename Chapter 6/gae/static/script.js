'use strict'

function formSubmit(event) { 
  log.textContent = `Form Submitted! Time stamp: ${event.timeStamp}`;
}

const go_form = document.getElementById('go-form');
const log = document.getElementById('log');

go_form.addEventListener('submit', formSubmit);
