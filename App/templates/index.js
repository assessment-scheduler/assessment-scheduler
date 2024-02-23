document.addEventListener('DOMContentLoaded', function() {

    var containerEl = document.getElementById('courses-list');

    for (var i = 1; i <= 5; i++) {
        var eventEl = document.createElement('div');
        eventEl.classList.add('fc-event', 'fc-h-event', 'fc-daygrid-event', 'fc-daygrid-block-event');
        eventEl.innerHTML = '<div class="fc-event-main">Assignment ' + i + '</div>';
        containerEl.appendChild(eventEl);
      }
    

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
      events : [
        {
          title:'Assignemnt 1',
          start:'2024-02-02',
          end: '2024-02-12',
        },
        // {% for event in events %}
        // {
        //     title : '{{event.todo}}',
        //     start : '{{event.date}}',
        // },
        // {% endfor %}
      ],
      eventResize:function(info){
        toEditItem(info.event);
      },
      eventDrop:function(info){
        calendarEventDragged(info.event)
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