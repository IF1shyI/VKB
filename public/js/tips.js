const bbruk = localStorage.getItem('Bensinbruk')
const Distans = localStorage.getItem('distance')
const Bpris = localStorage.getItem('Bensinpris')
const totprisbpris = localStorage.getItem('Totprisbensin')
const C02 = localStorage.getItem('C02')

const Hpris = bbruk * 0.8
const Lpris = bbruk * 0.7

const totfbrukH =Hpris * Distans
const totfbrukL =Lpris * Distans

const totprisH = totfbrukH * Bpris
const totprisL = totfbrukL * Bpris

const SparH = totprisbpris - totprisH
const SparL = totprisbpris - totprisL

const Tspar = (SparH + SparL)/2

const Co2sH = C02*0.3
const Co2sL = C02*0.2

const Co2tot = (Co2sH + Co2sL)/2

console.log('Har kört js för att hitta diff', SparH, SparL, Tspar)
const SparandeH = document.getElementById('SparH');
SparandeH.innerHTML = `${SparH.toFixed(0)}`;

const SparandeL = document.getElementById('SparL');
SparandeL.innerHTML = `${SparL.toFixed(0)}`;

const Totaltspar = document.getElementById('TotSpar')
Totaltspar.innerHTML = `${Tspar.toFixed(0)}`;

const Co2sparL =document.getElementById('co2sparL')
Co2sparL.innerHTML = `${Co2sL.toFixed(0)}`;

const Co2sparH =document.getElementById('co2sparH')
Co2sparH.innerHTML = `${Co2sH.toFixed(0)}`;

const C02Tot =document.getElementById('C02Tot')
C02Tot.innerHTML = `${Co2tot.toFixed(0)}`;