var weekCounter = 0;

document.addEventListener("DOMContentLoaded", function () {
  const colors = {
    Assignment: "#4a88c7",
    Quiz: "#4a88c7",
    Project: "#4a88c7",
    Exam: "#4a88c7",
    Presentation: "#4a88c7",
    Other: "#4a88c7",
    Pending: "#999999",
    Proctored: "#674ECC"
  };

  function formatDate(dateStr) {
    if (!dateStr) return null;
    
    if (typeof dateStr === 'string' && dateStr.includes('T')) {
      return dateStr.split('T')[0];
    }
    
    return dateStr;
  }

  const calendarEvents = (scheduledAssessments || [])
    .filter(assessment => assessment.scheduled !== null && assessment.scheduled !== undefined)
    .map(assessment => {
      let startDate = formatDate(assessment.scheduled);
      if (!startDate) return null;
      
      const isOwnedAssessment = staff_exams.some(exam => exam.id === assessment.id) || 
                               (myCourses && myCourses.some(course => course.code === assessment.course_code));
      
      return {
        id: assessment.id,
        title: `${assessment.course_code}-${assessment.name} (${assessment.percentage}%)`,
        start: startDate,
        allDay: true,
        backgroundColor: assessment.proctored ? colors.Proctored : colors.Assignment,
        textColor: '#fff',
        editable: isOwnedAssessment,
        extendedProps: {
          course_code: assessment.course_code,
          percentage: assessment.percentage,
          proctored: assessment.proctored,
          assessmentName: assessment.name,
          isOwnedAssessment: isOwnedAssessment
        }
      };
    })
    .filter(event => event !== null);

  const levelFilter = document.getElementById("level");
  const courseFilter = document.getElementById("courses");
  const typeFilter = document.getElementById("assignmentType");
  const calendarEl = document.getElementById("calendar");
  const unscheduledList = document.getElementById("unscheduled-list");
  const scheduledList = document.getElementById("scheduled-list");

  if (!calendarEl) return;

  if (unscheduledList) {
    new FullCalendar.Draggable(unscheduledList, {
      itemSelector: ".draggable-assessment",
      eventData: function(eventEl) {
        return {
          id: eventEl.dataset.assessmentId,
          title: `${eventEl.dataset.courseCode}-${eventEl.dataset.name || eventEl.children[0].innerText.split('-')[1]} (${eventEl.dataset.percentage}%)`,
          backgroundColor: eventEl.dataset.proctored === "1" ? colors.Proctored : colors.Assignment,
          textColor: '#fff',
          extendedProps: {
            course_code: eventEl.dataset.courseCode,
            percentage: eventEl.dataset.percentage,
            proctored: eventEl.dataset.proctored === "1",
          }
        };
      },
      mirrorSelector: ".draggable-assessment",
      dragRevertDuration: 0,
      droppableScope: 'assessment'
    });
  }

  if (scheduledList) {
    new FullCalendar.Draggable(scheduledList, {
      itemSelector: ".draggable-assessment",
      eventData: function(eventEl) {
        return {
          id: eventEl.dataset.assessmentId,
          title: `${eventEl.dataset.courseCode}-${eventEl.dataset.name || eventEl.children[0].innerText.split('-')[1]} (${eventEl.dataset.percentage}%)`,
          backgroundColor: eventEl.dataset.proctored === "1" ? colors.Proctored : colors.Assignment,
          textColor: '#fff',
          extendedProps: {
            course_code: eventEl.dataset.courseCode,
            percentage: eventEl.dataset.percentage,
            proctored: eventEl.dataset.proctored === "1",
          }
        };
      },
      mirrorSelector: ".draggable-assessment",
      dragRevertDuration: 0,
      droppableScope: 'assessment'
    });
  }

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: localStorage.getItem('calendarViewType') || "dayGridMonth",
    headerToolbar: {
      left: "prev,next,today",
      center: "title",
      right: "semesterView,dayGridMonth,timeGridWeek",
    },
    views: {
      semesterView: {
        type: "dayGridMonth",
        duration: { weeks: semesterWeeks },
        buttonText: "Semester",
        visibleRange: semester && semester.start_date && semester.end_date ? {
          start: semester.start_date,
          end: semester.end_date,
        } : null,
      },
      timeGridWeek: {
        allDaySlot: true,
        allDayText: 'Assessments',
        slotMinTime: "08:00:00",
        slotMaxTime: "20:00:00",
      }
    },
    height: 'auto',
    displayEventTime: false,
    allDaySlot: true,
    allDayText: 'Assessments',
    slotMinTime: "08:00:00",
    slotMaxTime: "20:00:00",
    editable: true,
    selectable: true,
    droppable: true,
    dayMaxEvents: false,
    
    // Allow events to be removed by dragging them out of the calendar
    eventStartEditable: true,
    eventDurationEditable: false,
    removable: true,
    droppableScope: 'assessment',
    dragRevertDuration: 0,
    dragScroll: true,
    dropAccept: '.draggable-assessment',
    
    // Set valid date range for the calendar
    validRange: semester && semester.start_date && semester.end_date ? {
      start: semester.start_date,
      end: semester.end_date
    } : null,
    
    // Callback to validate drops
    eventAllow: function(dropInfo, draggedEvent) {
      if (!semester || !semester.start_date || !semester.end_date) {
        return false;
      }
      
      const eventDate = dropInfo.start;
      const semesterStart = new Date(semester.start_date);
      const semesterEnd = new Date(semester.end_date);
      
      return eventDate >= semesterStart && eventDate <= semesterEnd;
    },
    
    // Save the current view when it changes
    viewDidMount: function(info) {
      localStorage.setItem('calendarViewType', info.view.type);
    },
    
    eventDidMount: function(info) {
      const eventEl = info.el;
      const eventContent = eventEl.querySelector('.fc-event-title');
      
      const isProctored = info.event.extendedProps?.proctored;
      const courseCode = info.event.extendedProps?.course_code || '';
      const percentage = info.event.extendedProps?.percentage || '';
      const assessmentName = info.event.extendedProps?.assessmentName || '';
      const isOwnedAssessment = info.event.extendedProps?.isOwnedAssessment;
      
      let html = `
        <div class="assessment-name">${courseCode}-${assessmentName}</div>
        <div class="assessment-details">
          Weight: ${percentage}%
          ${isProctored ? '<span class="badge">Proctored</span>' : ''}
        </div>
      `;
      
      if (eventContent) {
        eventContent.innerHTML = html;
      }
      
      eventEl.style.margin = '2px 0';
      eventEl.style.padding = '4px 8px';
      eventEl.style.height = 'auto';
      eventEl.style.minHeight = '50px';
      eventEl.style.width = '100%';
      
      if (isProctored) {
        eventEl.style.borderLeft = '4px solid #9C9FE2';
      } else {
        eventEl.style.borderLeft = '4px solid #fff';
      }
      
      if (!isOwnedAssessment) {
        eventEl.style.opacity = '0.6';
        eventEl.style.cursor = 'default';
        eventEl.style.pointerEvents = isOwnedAssessment ? 'auto' : 'none';
      }
      
      eventEl.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';
      eventEl.style.borderRadius = '4px';
      eventEl.style.transition = 'all 0.2s ease';
      
      if (isOwnedAssessment) {
        eventEl.addEventListener('mouseenter', function() {
          eventEl.style.boxShadow = '0 3px 6px rgba(0,0,0,0.3)';
          eventEl.style.transform = 'translateY(-2px)';
        });
        
        eventEl.addEventListener('mouseleave', function() {
          eventEl.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';
          eventEl.style.transform = 'translateY(0)';
        });
      }
      
      eventEl.title = info.event.title;
    },
    
    eventResize: handleEventEdit,
    eventDrop: handleEventDrop,
    drop: handleNewItem,
    eventReceive: function(info) {
      const tempEvent = info.event;
      
      if (!semester || !semester.start_date) {
        console.error('Semester start date not available');
        tempEvent.remove();
        alert("Cannot schedule assessment: No active semester found.");
        return;
      }
      
      const eventDate = tempEvent.start;
      const semesterStart = new Date(semester.start_date);
      const semesterEnd = new Date(semester.end_date);
      
      if (eventDate < semesterStart || eventDate > semesterEnd) {
        tempEvent.remove();
        alert("Cannot schedule assessment: Date is outside the semester range.");
        return;
      }
      
      const offsets = calculateWeekAndDayOffsets(tempEvent.start, semester.start_date);
      
      saveEvent({
        id: tempEvent.id,
        assessment_date: tempEvent.start.toISOString().split('T')[0],
        start_week: offsets.startWeek,
        start_day: offsets.startDay,
        end_week: offsets.endWeek,
        end_day: offsets.endDay
      }, tempEvent);
    },
    eventDragStop: function(info) {
      const calendarRect = calendarEl.getBoundingClientRect();
      const eventRect = info.jsEvent.target.getBoundingClientRect();
      
      if (eventRect.left < calendarRect.left || eventRect.right > calendarRect.right ||
          eventRect.top < calendarRect.top || eventRect.bottom > calendarRect.bottom) {
        
        if (!info.event.extendedProps.isOwnedAssessment) {
          alert("You can only unschedule assessments that belong to your courses.");
          return;
        }

        if (confirm("Are you sure you want to unschedule this assessment?")) {
          unscheduleEvent(info.event.id);
        } else {
          calendar.addEvent(info.event.toPlainObject());
        }
      }
    },
    eventRemove: function(info) {
      const eventId = info.event.id;
      unscheduleEvent(eventId);
    },
    eventLeave: function(info) {
      const eventId = info.event.id;
      unscheduleEvent(eventId);
    }
  });

  if (calendarEvents && calendarEvents.length > 0) {
    calendarEvents.forEach(event => {
      try {
        calendar.addEvent(event);
      } catch (e) {
        console.error(`Failed to add event ${event.id}:`, e);
      }
    });
  }

  try {
    calendar.render();
    
    setTimeout(() => calendar.refetchEvents(), 300);
  } catch (error) {
    console.error('Error rendering calendar:', error);
  }

  if (levelFilter) {
    levelFilter.addEventListener("change", function () {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
      updateCalendarEvents(calendar, filteredEvents);
    });
  }

  if (courseFilter) {
    courseFilter.addEventListener("change", function () {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
      updateCalendarEvents(calendar, filteredEvents);
    });
  }

  if (typeFilter) {
    typeFilter.addEventListener("change", function () {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
      updateCalendarEvents(calendar, filteredEvents);
    });
  }

  function filterEvents(level, courseCode, type) {
    let filteredEvents = scheduledAssessments || [];
    
    if (level !== "0") {
      filteredEvents = filteredEvents.filter(item => {
        return item.course_code && item.course_code[4] === level;
      });
    }
    
    if (courseCode !== "all") {
      if (courseCode === "My Courses") {
        const myAssessmentIds = staff_exams.map(exam => exam.id.toString());
        filteredEvents = filteredEvents.filter(item => myAssessmentIds.includes(item.id.toString()));
      } else {
        filteredEvents = filteredEvents.filter(item => item.course_code === courseCode);
      }
    }
    
    if (type !== "all") {
      const isProctored = type === "1";
      filteredEvents = filteredEvents.filter(item => (item.proctored == isProctored));
    }
    
    return filteredEvents;
  }

  function updateCalendarEvents(calendar, newEvents) {
    calendar.removeAllEvents();
    
    const updatedEvents = newEvents
      .filter(assessment => assessment.scheduled !== null && assessment.scheduled !== undefined)
      .map(assessment => {
        let startDate = formatDate(assessment.scheduled);
        if (!startDate) return null;
        
        const isOwnedAssessment = staff_exams.some(exam => exam.id === assessment.id) || 
                                 (myCourses && myCourses.some(course => course.code === assessment.course_code));
        
        return {
          id: assessment.id,
          title: `${assessment.course_code}-${assessment.name} (${assessment.percentage}%)`,
          start: startDate,
          allDay: true,
          backgroundColor: assessment.proctored ? colors.Proctored : colors.Assignment,
          textColor: '#fff',
          editable: isOwnedAssessment,
          extendedProps: {
            course_code: assessment.course_code,
            percentage: assessment.percentage,
            proctored: assessment.proctored,
            assessmentName: assessment.name,
            isOwnedAssessment: isOwnedAssessment
          }
        };
      })
      .filter(event => event !== null);
    
    updatedEvents.forEach(event => {
      calendar.addEvent(event);
    });
    
    calendar.refetchEvents();
  }

  function calculateWeekAndDayOffsets(date, semesterStartDate) {
    const assessmentDate = new Date(date);
    const startDate = new Date(semesterStartDate);
    
    const dayDiff = Math.floor((assessmentDate - startDate) / (1000 * 60 * 60 * 24));
    
    const weekOffset = Math.floor(dayDiff / 7) + 1; 
    
    let dayOffset = assessmentDate.getDay();
    if (dayOffset === 0) {
      dayOffset = 7;  
    }
    
    return {
      startWeek: weekOffset,
      startDay: dayOffset,
      endWeek: weekOffset,
      endDay: dayOffset
    };
  }

  function handleEventEdit(info) {
    const event = info.event;
    const newDate = event.start;
    
    if (!semester || !semester.start_date) {
      console.error('Semester start date not available');
      return;
    }
    
    const offsets = calculateWeekAndDayOffsets(newDate, semester.start_date);
    
    saveEvent({
      id: event.id,
      assessment_date: newDate.toISOString().split('T')[0],
      start_week: offsets.startWeek,
      start_day: offsets.startDay,
      end_week: offsets.endWeek,
      end_day: offsets.endDay
    });
  }

  function handleEventDrop(info) {
    // Check if the new date is within the semester range
    const eventDate = info.event.start;
    const semesterStart = new Date(semester.start_date);
    const semesterEnd = new Date(semester.end_date);
    
    if (eventDate < semesterStart || eventDate > semesterEnd) {
      info.revert();
      alert("Cannot schedule assessment: Date is outside the semester range.");
      return;
    }
    
    handleEventEdit(info);
  }

  function handleNewItem(info) {
    return;
  }

  function saveEvent(data, tempEvent = null) {
    const currentLevel = levelFilter.value;
    const currentCourse = courseFilter.value;
    const currentType = typeFilter.value;

    if (!data.assessment_date && tempEvent && tempEvent.start) {
      data.assessment_date = tempEvent.start.toISOString().split('T')[0];
      
      if (semester && semester.start_date) {
        const offsets = calculateWeekAndDayOffsets(tempEvent.start, semester.start_date);
        data.start_week = offsets.startWeek;
        data.start_day = offsets.startDay;
        data.end_week = offsets.endWeek;
        data.end_day = offsets.endDay;
      }
    }

    console.log('Sending assessment update:', {
      id: data.id,
      date: data.assessment_date,
      start_week: data.start_week,
      start_day: data.start_day,
      end_week: data.end_week,
      end_day: data.end_day
    });

    const formattedData = {
      id: parseInt(data.id),
      assessment_date: data.assessment_date,
      start_week: parseInt(data.start_week),
      start_day: parseInt(data.start_day),
      end_week: parseInt(data.end_week),
      end_day: parseInt(data.end_day)
    };

    // Create a form and submit it
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/update_assessment_schedule';
    form.style.display = 'none';
    
    for (const key in formattedData) {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = key;
      input.value = formattedData[key];
      form.appendChild(input);
    }
    
    document.body.appendChild(form);
    form.submit();
  }

  function unscheduleEvent(eventId) {
    // Create a form and submit it to unschedule the assessment
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/unschedule_assessment';
    form.style.display = 'none';
    
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'id';
    input.value = eventId;
    form.appendChild(input);
    
    document.body.appendChild(form);
    form.submit();
  }

  const disclaimerText = document.createElement("div");
  disclaimerText.textContent = "Page may occasionally refresh on calendar input";
  disclaimerText.style.color = "#666";
  disclaimerText.style.fontSize = "12px";
  disclaimerText.style.marginBottom = "8px";
  disclaimerText.style.textAlign = "center";
  disclaimerText.style.fontStyle = "italic";

  const autoscheduleButton = document.createElement("button");
  autoscheduleButton.textContent = "Autoschedule ALL";
  autoscheduleButton.className = "btn mb-3";
  autoscheduleButton.style.width = "100%";
  autoscheduleButton.style.backgroundColor = "#5c46b4";
  autoscheduleButton.style.color = "white";
  autoscheduleButton.style.padding = "12px";
  autoscheduleButton.style.fontWeight = "bold";
  autoscheduleButton.style.border = "none";
  
  if (unscheduledList) {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/autoschedule";
    form.style.width = "100%";
    form.style.marginBottom = "1rem";
    
    form.appendChild(disclaimerText);
    form.appendChild(autoscheduleButton);
    
    unscheduledList.parentNode.insertBefore(form, unscheduledList);
    
    form.addEventListener("submit", function(e) {
      e.preventDefault();
      
      const modalOverlay = document.createElement('div');
      modalOverlay.style.position = 'fixed';
      modalOverlay.style.top = '0';
      modalOverlay.style.left = '0';
      modalOverlay.style.width = '100%';
      modalOverlay.style.height = '100%';
      modalOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
      modalOverlay.style.display = 'flex';
      modalOverlay.style.justifyContent = 'center';
      modalOverlay.style.alignItems = 'center';
      modalOverlay.style.zIndex = '9999';
      
      const modalContent = document.createElement('div');
      modalContent.style.backgroundColor = '#5c46b4';
      modalContent.style.padding = '2rem';
      modalContent.style.borderRadius = '8px';
      modalContent.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
      modalContent.style.maxWidth = '400px';
      modalContent.style.width = '90%';
      modalContent.style.position = 'relative';
      modalContent.style.color = 'white';
      
      const modalHeader = document.createElement('div');
      modalHeader.style.marginBottom = '1.5rem';
      modalHeader.innerHTML = `
        <h3 style="margin: 0; font-size: 1.5rem; font-weight: bold;">
          ⚠️ Autoschedule Confirmation
        </h3>
      `;
      
      const modalBody = document.createElement('div');
      modalBody.style.marginBottom = '1.5rem';
      modalBody.innerHTML = `
        <p style="margin-bottom: 1rem; line-height: 1.5;">
          This will automatically schedule all unscheduled assessments. The process may take up to a minute to complete.
        </p>
      `;
      
      const modalFooter = document.createElement('div');
      modalFooter.style.display = 'flex';
      modalFooter.style.justifyContent = 'flex-end';
      modalFooter.style.gap = '1rem';
      
      const cancelButton = document.createElement('button');
      cancelButton.textContent = 'Cancel';
      cancelButton.className = 'btn';
      cancelButton.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
      cancelButton.style.color = 'white';
      cancelButton.style.border = '1px solid white';
      cancelButton.style.padding = '8px 16px';
      cancelButton.style.borderRadius = '4px';
      cancelButton.style.cursor = 'pointer';
      
      const confirmButton = document.createElement('button');
      confirmButton.textContent = 'Proceed';
      confirmButton.className = 'btn';
      confirmButton.style.backgroundColor = 'white';
      confirmButton.style.color = '#5c46b4';
      confirmButton.style.border = 'none';
      confirmButton.style.padding = '8px 16px';
      confirmButton.style.borderRadius = '4px';
      confirmButton.style.cursor = 'pointer';
      
      modalFooter.appendChild(cancelButton);
      modalFooter.appendChild(confirmButton);
      
      modalContent.appendChild(modalHeader);
      modalContent.appendChild(modalBody);
      modalContent.appendChild(modalFooter);
      modalOverlay.appendChild(modalContent);
      
      document.body.appendChild(modalOverlay);
      
      cancelButton.onclick = function() {
        document.body.removeChild(modalOverlay);
      };
      
      confirmButton.onclick = function() {
        document.body.removeChild(modalOverlay);
        autoscheduleButton.disabled = true;
        autoscheduleButton.textContent = "Scheduling...";
        autoscheduleButton.style.backgroundColor = "#5c46b4";
        
        form.submit();
        
        setTimeout(() => {
          if (autoscheduleButton.disabled) {
            autoscheduleButton.disabled = false;
            autoscheduleButton.textContent = "Autoschedule ALL";
            autoscheduleButton.style.backgroundColor = "#5c46b4";
            alert("The scheduling process is still running in the background. Please refresh the page in a few moments to see the results.");
          }
        }, 60000);
      };
      
      modalOverlay.onclick = function(event) {
        if (event.target === modalOverlay) {
          document.body.removeChild(modalOverlay);
        }
      };
    });
  }

  const filters = document.getElementById("filters");
  if (filters) {
    filters.style.marginBottom = '20px';
    
    const selects = filters.querySelectorAll('select');
    selects.forEach(select => {
      select.style.backgroundColor = '#5c46b4';
      select.style.color = 'white';
      select.style.border = '1px solid #5c46b4';
      select.style.borderRadius = '4px';
      select.style.padding = '8px 12px';
      select.style.margin = '0 8px 8px 0';
      select.style.cursor = 'pointer';
      select.style.fontWeight = '500';
      
      const options = select.querySelectorAll('option');
      options.forEach(option => {
        option.style.backgroundColor = '#5c46b4';
      });
    });
  }
}); 