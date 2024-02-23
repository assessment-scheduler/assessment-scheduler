document.addEventListener('DOMContentLoaded', function() {
    eventNames=["Assignment 1", "Assignment 2", "Coursework Exam", "Lab Exam", "Project"];
    courseCodes=["COMP 1601", "COMP 1602", "INFO 1600"];

    courseCodes.forEach((courseCode) => {
        const courseCard = document.createElement('div');
        courseCard.classList.add('course-card'); // Add styling for the course card
    
        const title = document.createElement('h3');
        title.textContent = courseCode;
        courseCard.appendChild(title);
    
        // Create a container for events within this course
        const eventsContainer = document.createElement('div');
        eventsContainer.classList.add('course-events'); // Add styling for the events container
    
        // Loop through each event name and create an event element
        eventNames.forEach((eventName) => {
          const eventEl = document.createElement('div');
          eventEl.classList.add('fc-event', 'fc-h-event', 'fc-daygrid-event', 'fc-daygrid-block-event');
          eventEl.innerHTML = '<div class="fc-event-main">' + eventName + '</div>';
          eventsContainer.appendChild(eventEl);
        });
    
        courseCard.appendChild(eventsContainer);
        document.getElementById('courses-list').appendChild(courseCard);
      });
    
    var containerEl = document.getElementById('courses-list');      
    new FullCalendar.Draggable(containerEl, {
      itemSelector: '.fc-event',
      eventData: function(eventEl) {
        return {
          title: eventEl.innerText.trim()
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
        calendarEventDragged(info.event)
      },
      drop: function(arg) {
          arg.draggedEl.parentNode.removeChild(arg.draggedEl);
      }
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