import {carData} from './Sokreg.js';


const Hpris = carData.bbruk * 0.8
const Lpris = carData.bbruk * 0.7

const totfbrukH =Hpris * carData.distance
const totfbrukL =Lpris * carData.distance

const totprisH = totfbrukH * carData.bensinpris
const totprisL = totfbrukL * carData.bensinpris

const SparH = carData.bensinkostnad_tot - totprisH
const SparL = carData.bensinkostnad_tot - totprisL

const SparandeH = document.getElementById('SparH');
SparandeH.innerHTML = `<p>${SparH.toFixed(2)}</p>`;

const SparandeL = document.getElementById('SparL');
SparandeL.innerHTML = `<p>${SparL.toFixed(2)}</p>`;
