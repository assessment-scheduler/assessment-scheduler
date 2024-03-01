document.addEventListener('DOMContentLoaded', function() {
    course1=["COMP 1601", "Assignment 1", "Assignment 2", "Coursework Exam"]
    course2=["COMP 1602", "Assignment 1", "Assignment 2", "Coursework Exam 1", "Coursework Exam 2"]
    course3=["INFO 2604", "Assignment 1", "Assignment 2", "Coursework Exam", "Project"]
    courses=[course1,course2,course3]
    const colors = {
      Assignment:"#3397b9", 
      Quiz:"#499373", 
      Project:"#006064", 
      Exam:"#CC4E4E", 
      Presentation:"#cc7a50",
      Other:"#C29203"
    }
    index=0;

    courses.forEach((course) => {
        const courseCard = document.createElement('div');
        courseCard.classList.add('course-card'); // Add styling for the course card     

        const title = document.createElement('h3');
        title.textContent = course[0];
        courseCard.appendChild(title);
    
        // Create a container for events within this course
        const eventsContainer = document.createElement('div');
        eventsContainer.classList.add('course-events'); // Add styling for the events container

        var assessments=course.slice(1);
        // Loop through each event name and create an event element
        assessments.forEach((eventName) => {
          const eventEl = document.createElement('div');
          eventEl.classList.add('fc-event', 'fc-h-event', 'fc-daygrid-event', 'fc-daygrid-block-event');

          const typeOfAssessment = getTypeOfAssessment(eventName);
          color = colors[typeOfAssessment];

          eventEl.dataset.color = color;
          eventEl.style.backgroundColor = color;
      
          eventEl.innerHTML = '<div class="fc-event-main">' + course[0] + '-' + eventName + '</div>';
          eventsContainer.appendChild(eventEl);
        });
    
        index++;
        courseCard.appendChild(eventsContainer);
        document.getElementById('courses-list').appendChild(courseCard);
      });
    
    var containerEl = document.getElementById('courses-list');      
    new FullCalendar.Draggable(containerEl, {
      itemSelector: '.fc-event',
      eventData: function(eventEl) {
        return {
          title: eventEl.innerText.trim(),
          backgroundColor: eventEl.dataset.color
        }
      }
    });

    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth',
      headerToolbar: {
        left:'prev,next,today',
        center: 'title',    
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
      editable:true,
      selectable:true,
      droppable:true,
        // {% for event in events %}
        // {
        //     title : '{{event.todo}}',
        //     start : '{{event.date}}',
        // },
        // {% endfor %}
      eventResize:function(info){
        toEditItem(info.event);
      },
      eventDrop:function(info){
        calendarEventDragged(info.event);
      },
      drop: function(arg) {
          arg.draggedEl.parentNode.removeChild(arg.draggedEl);
      },
    });
    calendar.render();
  });


  
function calendarEventDragged(event){
    let id=event.id;
    let sDate=formatDate(new Date(event.start));
    let eDate=formatDate(new Date(event.end));
    console.log(sDate);
    console.log(eDate);
}

function toEditItem(event){
    let id=event.id;
    let sDate=formatDate(new Date(event.start));
    let eDate=formatDate(new Date(event.end));
    console.log(sDate);
    console.log(eDate);
}

function formatDate(dateObj){
    let year=dateObj.getFullYear();
    let month=dateObj.getMonth()+1;
    let day=dateObj.getDate();

    let paddedMonth=month.toString()
    if (paddedMonth.length < 2){
        paddedMonth="0"+paddedMonth;
    }

    let paddedDate=day.toString()
    if (paddedDate.length < 2){
        paddedDate="0"+paddedDate;
    }

    let toStoreDate=`${year}-${paddedMonth}-${paddedDate}`;
    return toStoreDate;
}

function getTypeOfAssessment(eventName) {
  if (eventName.toLowerCase().includes("assignment")) {
      return "Assignment";
  } else if (eventName.toLowerCase().includes("exam")) {
      return "Exam";
  } else if (eventName.toLowerCase().includes("project")) {
      return "Project";
  } else if (eventName.toLowerCase().includes("quiz")) {
      return "Quiz";
  } else if (eventName.toLowerCase().includes("presentation")) {
      return "Presentation";
  }
  return "Other";
}