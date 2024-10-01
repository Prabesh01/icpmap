function updateAuthorPercentage() {
  const authorElements = document.getElementsByClassName("author-wrapper");

  Array.from(authorElements).forEach(element => {
      const percentage = element.getAttribute("data-per");

      if (percentage) {
          const svgContent = `<svg viewBox="0 0 64 64" class="pie">
                                  <circle r="25%" cx="50%" cy="50%" style="stroke-dasharray: ${percentage} 100"></circle>
                              </svg>`;
          const figCaption = `<figcaption>${percentage}%</figcaption>`;
          element.innerHTML = `${svgContent}${figCaption}`;
      }
  });
}

window.onload = updateAuthorPercentage;

const currentDate = new Date();
const options = { weekday: 'long', day: 'numeric', month: 'long'};
const formattedDate = currentDate.toLocaleDateString('en-US', options);

document.getElementById("date").innerHTML = `📅 ${formattedDate} ${currentDate.getFullYear()}`;

var nearestExam=365;
var nearestExam2=365;

var allCount=soonCount=upcomingCount=expiredCount=0;
const allCountDiv=document.getElementById("allCount");
allCountDiv.innerHTML = "All: 0";
const soonCountDiv=document.getElementById("soonCount");
soonCountDiv.innerHTML = "Soon: 0";
const upcomingCountDiv=document.getElementById("upcomingCount");
upcomingCountDiv.innerHTML = "Upcoming: 0";
const expiredCountDiv=document.getElementById("expiredCount");
expiredCountDiv.innerHTML = "Expired: 0";
const divList=[allCountDiv,soonCountDiv,upcomingCountDiv,expiredCountDiv];
var cantChange=false;

function showDiv(clas1,clas2=clas1){	
if(clas1!="guide-slot_card" || clas2!="guide-slot_card"){cantChange=true;}
Array.from(document.getElementsByClassName("guide-slot")).forEach(function(element) {
  var curelement=element.getElementsByClassName("guide-slot_card")[0].classList
  if(curelement.contains(clas1) || curelement.contains(clas2)){
    element.classList.remove("hide");
    element.classList.remove("invisible");
  }else{
    element.classList.add("hide");
    if(clas2!=clas1){element.classList.add("invisible");}
    setTimeout(function(){
  element.classList.add("invisible");
cantChange=false;
}, 1500); 

  }
});
}

function selectDiv(div1,div2=div1){
var i=0;
divList.forEach(function(element) {
  if(i==div1 || i==div2){element.classList.add("selected");}
  else{element.classList.remove("selected");}
  i++;
});
}

function initialStat(){
selectBoth();
//selectDiv(1);
//showDiv('soon');
}

function selectBoth(){
selectDiv(1,2);
showDiv('soon','upcoming');
}

allCountDiv.onclick = function() { if(cantChange){return;} selectDiv(0); showDiv('guide-slot_card') };
soonCountDiv.onclick = function() { if(cantChange){return;} selectDiv(1); showDiv('soon') };
upcomingCountDiv.onclick = function() { if(cantChange){return;} selectDiv(2);  showDiv('upcoming') };
expiredCountDiv.onclick = function() { if(cantChange){return;} if(expiredCountDiv.classList.contains('selected')){selectBoth();}else{selectDiv(3);  showDiv('expired');} };


function updateEventStatus() {
  const currentDate = new Date();
  const scheduleStages = document.querySelectorAll('.guide-slot_card[data-date]');

  scheduleStages.forEach(scheduleStage => {
      const eventDate = new Date(scheduleStage.getAttribute("data-date"));
      const eventStatusElement = scheduleStage.querySelector('.event-status');
      const remainingDaysElement = scheduleStage.querySelector('.remaining-days');

      const timeDifference = (eventDate - currentDate);
      const daysUntilExam = Math.floor(timeDifference / (1000 * 60 * 60 * 24)) +1;
  
  
  if (daysUntilExam >= 0) {
    if (daysUntilExam==nearestExam){}
  else if(daysUntilExam<nearestExam){
    nearestExam2=nearestExam;
    nearestExam=daysUntilExam;
  } else if(daysUntilExam<nearestExam2){
    nearestExam2=daysUntilExam;
  }

  document.getElementById("nextExam").innerHTML = `Next Exam in: ${nearestExam} days and ${nearestExam2} days`;
  }
  allCount++;
  allCountDiv.innerHTML = "All: "+allCount;
      if (daysUntilExam <= 30 && daysUntilExam >= 0) {
          // New event (within 30 days of the current date)
    soonCount++;
    soonCountDiv.innerHTML = "Soon: "+soonCount;			
          scheduleStage.classList.add("soon");
          eventStatusElement.textContent = "soon";
          remainingDaysElement.textContent = `(${Math.abs(daysUntilExam)} days)`;
      } else if (eventDate > currentDate) {
          // Upcoming event
    upcomingCount++;
    upcomingCountDiv.innerHTML = "Upcoming: "+upcomingCount;
          scheduleStage.classList.add("upcoming");
          eventStatusElement.textContent = "upcoming";
          remainingDaysElement.textContent = `(${daysUntilExam} days)`;
      } else {
          // Expired event
    expiredCount++;
    expiredCountDiv.innerHTML = "Expired: "+expiredCount;			
          scheduleStage.classList.add("expired");
          eventStatusElement.textContent = "Expired";
          remainingDaysElement.textContent = ""; // No need to show remaining days for expired events
      }
  });
}

document.getElementById('class_drop').addEventListener('change', function() {
  const selectedDate = this.value;

  if (selectedDate) {
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = window.location.href;

      const hiddenField = document.createElement('input');
      hiddenField.type = 'hidden';
      hiddenField.name = 'class';
      hiddenField.value = selectedDate;

      form.appendChild(hiddenField);
      document.body.appendChild(form);
      form.submit();
  }
});

window.history.pushState({}, '', window.location.href);

updateEventStatus();
initialStat();