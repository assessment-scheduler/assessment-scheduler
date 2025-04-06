var weekCounter = 0;

// Global variables for handling assessment scheduling
let pendingScheduleData = null;
let pendingEvent = null;

document.addEventListener("DOMContentLoaded", function () {
  let eventsLoaded = false;
  
  console.log("Calendar init - Semester dates:", semester);
  if (semester && semester.start_date && semester.end_date) {
    console.log("Start date:", new Date(semester.start_date));
    console.log("End date:", new Date(semester.end_date));
  }
  
  // Debug information: Print all scheduled assessments details
  console.log("============ SCHEDULED ASSESSMENTS DEBUG INFO ============");
  console.log(`Total scheduled assessments: ${scheduledAssessments ? scheduledAssessments.length : 0}`);
  if (scheduledAssessments && scheduledAssessments.length > 0) {
    console.table(scheduledAssessments.map(assessment => ({
      id: assessment.id,
      course: assessment.course_code,
      name: assessment.name,
      date: assessment.scheduled,
      percentage: assessment.percentage,
      proctored: assessment.proctored ? "Yes" : "No",
      week: assessment.start_week,
      day: assessment.start_day
    })));
    
    // Group by course
    const courseGroups = {};
    scheduledAssessments.forEach(assessment => {
      if (!courseGroups[assessment.course_code]) {
        courseGroups[assessment.course_code] = [];
      }
      courseGroups[assessment.course_code].push(assessment);
    });
    
    console.log("Scheduled assessments by course:");
    Object.keys(courseGroups).forEach(courseCode => {
      console.log(`${courseCode}: ${courseGroups[courseCode].length} assessments`);
      console.group(courseCode);
      courseGroups[courseCode].forEach(assessment => {
        console.log(`${assessment.name} - ${assessment.scheduled} - ${assessment.percentage}%${assessment.proctored ? " (Proctored)" : ""}`);
      });
      console.groupEnd();
    });
  } else {
    console.log("No scheduled assessments found.");
  }
  console.log("=======================================================");
  
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
    
    console.log("Formatting date:", dateStr, "Type:", typeof dateStr);
    
    try {
      // Handle ISO string format
    if (typeof dateStr === 'string' && dateStr.includes('T')) {
      return dateStr.split('T')[0];
    }
      
      // Handle date object
      if (dateStr instanceof Date) {
        return dateStr.toISOString().split('T')[0];
      }
      
      // Handle string date without T
      if (typeof dateStr === 'string' && dateStr.match(/^\d{4}-\d{2}-\d{2}/)) {
        return dateStr.substring(0, 10);
    }
    
    return dateStr;
    } catch (error) {
      console.error("Error formatting date:", error, dateStr);
      return null;
    }
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
    console.log("Initializing drag for assessments in My Assessments list");
    
    // Find all draggable items (both scheduled and unscheduled)
    const draggableItems = unscheduledList.querySelectorAll('.draggable-assessment.can-drag');
    console.log(`Found ${draggableItems.length} draggable assessments`);
    
    // More detailed logging to debug draggable elements
    const allItems = unscheduledList.querySelectorAll('.draggable-assessment');
    console.log(`Total items in list: ${allItems.length}`);
    console.log(`Unscheduled items: ${unscheduledList.querySelectorAll('.status-unscheduled').length}`);
    console.log(`Scheduled items: ${unscheduledList.querySelectorAll('.scheduled').length}`);
    
    // Log first few items for debugging
    if (draggableItems.length > 0) {
      console.log("Sample draggable item:", draggableItems[0]);
      console.log("Sample item data:", draggableItems[0].dataset);
    } else {
      console.warn("NO DRAGGABLE ITEMS FOUND - check class names!");
      
      // Fallback to any assessment
      const anyAssessment = unscheduledList.querySelectorAll('.draggable-assessment');
      if (anyAssessment.length > 0) {
        console.log("Found assessments without can-drag class:", anyAssessment.length);
        console.log("Sample assessment item:", anyAssessment[0]);
      }
    }
    
    // Improved draggable initialization with better feedback
    new FullCalendar.Draggable(unscheduledList, {
      itemSelector: ".draggable-assessment.can-drag",
      eventData: function(eventEl) {
        console.log("Dragging assessment:", eventEl.dataset);
        return {
          id: eventEl.dataset.assessmentId,
          title: `${eventEl.dataset.courseCode}-${eventEl.dataset.name || eventEl.children[0].innerText.split('-')[1]} (${eventEl.dataset.percentage}%)`,
          backgroundColor: eventEl.dataset.proctored === "1" || eventEl.dataset.proctored === "True" || eventEl.dataset.proctored === "true" ? colors.Proctored : colors.Assignment,
          textColor: '#fff',
          extendedProps: {
            course_code: eventEl.dataset.courseCode,
            percentage: eventEl.dataset.percentage,
            proctored: eventEl.dataset.proctored === "1" || eventEl.dataset.proctored === "True" || eventEl.dataset.proctored === "true",
            isRescheduling: eventEl.classList.contains('scheduled')
          }
        };
      },
      mirrorSelector: ".draggable-assessment",
      dragRevertDuration: 0,
      droppableScope: 'assessment',
      dragClass: 'is-dragging',
      mirrorClass: 'assessment-mirror',
      // Add animation effects and feedback during dragging
      elementDragging: function(el, event) {
        // Highlight valid drop targets on drag start
        document.querySelectorAll('.fc-day').forEach(day => {
          day.classList.add('potential-drop-target');
        });
      },
      elementDragStop: function(el, event) {
        // Remove highlights when dragging stops
        document.querySelectorAll('.fc-day').forEach(day => {
          day.classList.remove('potential-drop-target');
          day.classList.remove('active-drop-target');
        });
      }
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

  // Add draggable functionality to the expanded assessment list
  const allAssessmentsList = document.getElementById("all-assessments");
  if (allAssessmentsList) {
    console.log("Initializing drag for expanded assessments list");
    new FullCalendar.Draggable(allAssessmentsList, {
      itemSelector: ".draggable-assessment",
      eventData: function(eventEl) {
        console.log("Dragging assessment from expanded list:", eventEl.dataset);
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
      droppableScope: 'assessment',
      dragClass: 'is-dragging',
      mirrorClass: 'assessment-mirror',
      elementDragging: function(el, event) {
        // Highlight valid drop targets on drag start
        document.querySelectorAll('.fc-day').forEach(day => {
          day.classList.add('potential-drop-target');
        });
      },
      elementDragStop: function(el, event) {
        // Remove highlights when dragging stops
        document.querySelectorAll('.fc-day').forEach(day => {
          day.classList.remove('potential-drop-target');
          day.classList.remove('active-drop-target');
        });
      }
    });
  }

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",  // Use standard month view initially
    headerToolbar: {
      left: "prev,next,today",
      center: "title",
      right: "dayGridMonth,timeGridWeek",
    },
    customButtons: {
      fullSemester: {
        text: 'Full Semester',
        click: function() {
          if (semester && semester.start_date && semester.end_date) {
            console.log("Showing full semester range:", semester.start_date, "to", semester.end_date);
            
            const startDate = new Date(semester.start_date);
            const endDate = new Date(semester.end_date);
            
            // Calculate the number of months to display
            const monthDiff = (endDate.getFullYear() - startDate.getFullYear()) * 12 + 
                              (endDate.getMonth() - startDate.getMonth()) + 1;
            
            console.log("Number of months in semester:", monthDiff);
            
            // Use multiMonth view to show all months in the semester
            calendar.setOption('multiMonthMaxColumns', 3); // Adjust based on screen size
            calendar.setOption('multiMonthMinWidth', 250); // Adjust based on preference
            
            calendar.gotoDate(startDate);
            calendar.changeView('multiMonth', {
              duration: { months: monthDiff }
            });
          }
        }
      }
    },
    views: {
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
    dayMaxEvents: 2, // Limit visible events to 2 per day
    
    // Improved drop handling for better UX
    dragRevert: true, // Revert drag if not dropped successfully
    dragScroll: true, // Auto-scroll while dragging
    longPressDelay: 150, // Make touch interactions more responsive
    eventLongPressDelay: 150, // Also for events
    
    // Change cursors to indicate draggability
    eventDragStart: function(info) {
      document.body.style.cursor = 'grabbing';
      info.el.style.cursor = 'grabbing';
      
      // Add visual effect for dragging
      info.el.classList.add('being-dragged');
      info.el.style.boxShadow = '0 6px 10px rgba(0,0,0,0.3)';
      info.el.style.transform = 'scale(1.05)';
      
      // Highlight calendar days when dragging starts
      document.querySelectorAll('.fc-day').forEach(day => {
        const dayDate = new Date(day.getAttribute('data-date'));
        if (semester && dayDate) {
          const semesterStart = new Date(semester.start_date);
          const semesterEnd = new Date(semester.end_date);
          if (dayDate >= semesterStart && dayDate <= semesterEnd) {
            day.classList.add('drop-target-highlight');
          }
        }
      });
    },
    
    eventDragStop: function(info) {
      document.body.style.cursor = '';
      info.el.style.cursor = '';
      
      // Remove visual dragging effect
      info.el.classList.remove('being-dragged');
      info.el.style.boxShadow = '';
      info.el.style.transform = '';
      
      // Remove highlights
      document.querySelectorAll('.fc-day').forEach(day => {
        day.classList.remove('drop-target-highlight');
      });
    },
    
    // Configure the "more" events popover
    moreLinkClick: 'popover',
    eventPopoverDidMount: function(info) {
      // Make the popover content larger and scrollable
      const popoverContent = info.el.querySelector('.fc-popover-body');
      if (popoverContent) {
        popoverContent.style.maxHeight = '300px';
        popoverContent.style.overflowY = 'auto';
        popoverContent.style.padding = '10px';
      }
      
      // Make sure the popover doesn't block dropping
      info.el.addEventListener('mouseenter', function() {
        // Set a short timeout to hide the popover when users are dragging
        const dragStartHandler = function() {
          info.el.style.display = 'none';
          document.removeEventListener('dragstart', dragStartHandler);
        };
        
        document.addEventListener('dragstart', dragStartHandler);
      });
    },
    
    // Add hover effects for calendar days during drag operations
    dayCellDidMount: function(info) {
      const cell = info.el;
      
      // Add hover listeners for drag preview
      cell.addEventListener('dragenter', function(e) {
        // Check if we're currently dragging an assessment
        if (document.querySelector('.is-dragging') || document.querySelector('.fc-event-dragging')) {
          cell.classList.add('active-drop-target');
          
          // Show a preview of where the assessment would be placed
          const dateStr = cell.getAttribute('data-date');
          if (dateStr) {
            // Create or update preview element
            let preview = cell.querySelector('.drop-preview');
            if (!preview) {
              preview = document.createElement('div');
              preview.className = 'drop-preview';
              preview.innerHTML = '<span>Drop assessment here</span>';
              cell.appendChild(preview);
            }
          }
        }
      });
      
      cell.addEventListener('dragleave', function(e) {
        cell.classList.remove('active-drop-target');
        
        // Remove preview
        const preview = cell.querySelector('.drop-preview');
        if (preview) {
          preview.remove();
        }
      });
      
      cell.addEventListener('dragover', function(e) {
        // Required to allow dropping
        e.preventDefault();
      });
      
      // For touch devices
      cell.addEventListener('touchmove', function(e) {
        const touch = e.touches[0];
        const elementAtTouch = document.elementFromPoint(touch.clientX, touch.clientY);
        
        // If we're over a calendar day
        if (elementAtTouch && elementAtTouch.classList.contains('fc-daygrid-day')) {
          // Remove active state from all days
          document.querySelectorAll('.fc-daygrid-day').forEach(day => {
            day.classList.remove('active-drop-target');
          });
          
          // Add active state to current day
          elementAtTouch.classList.add('active-drop-target');
        }
      });
    },
    
    eventStartEditable: true,
    eventDurationEditable: false,
    removable: true,
    droppableScope: 'assessment',
    dragRevertDuration: 0,
    dropAccept: '.draggable-assessment',
    
    eventAllow: function(dropInfo, draggedEvent) {
      if (!semester || !semester.start_date || !semester.end_date) {
        return false;
      }
      
      const eventDate = dropInfo.start;
      const semesterStart = new Date(semester.start_date);
      const semesterEnd = new Date(semester.end_date);
      
      return eventDate >= semesterStart && eventDate <= semesterEnd;
    },
    
    viewDidMount: function(info) {
      // Only store dayGridMonth and timeGridWeek views in localStorage
      if (info.view.type === 'dayGridMonth' || info.view.type === 'timeGridWeek') {
      localStorage.setItem('calendarViewType', info.view.type);
      }
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
          <div class="badge-container">
            ${isProctored ? '<span class="badge proctored">Proctored</span>' : ''}
          </div>
        </div>
      `;
      
      // Add delete button for owned assessments
      if (isOwnedAssessment) {
        html += `<button class="delete-assessment-btn" title="Unschedule assessment">&times;</button>`;
      }
      
      if (eventContent) {
        eventContent.innerHTML = html;
      }
      
      // Add event listener for delete button
      const deleteBtn = eventEl.querySelector('.delete-assessment-btn');
      if (deleteBtn) {
        deleteBtn.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          
          // Show confirmation dialog
          showUnscheduleConfirmation(info.event.id, courseCode, assessmentName);
        });
      }
      
      // Use our unified card styling
      eventEl.classList.add('calendar-event');
      
      // Set appropriate border-left color based on proctored status
      if (isProctored) {
        eventEl.style.borderLeftColor = '#9C9FE2';
      } else {
        eventEl.style.borderLeftColor = '#4a88c7';
      }
      
      // Adjust interaction based on ownership
      if (!isOwnedAssessment) {
        eventEl.style.opacity = '0.6';
        eventEl.style.cursor = 'default';
        eventEl.style.pointerEvents = 'none';
      } else {
        eventEl.title = 'Drag to reschedule';
        eventEl.style.cursor = 'pointer';
      }
    },
    
    eventResize: handleEventEdit,
    eventDrop: handleEventDrop,
    drop: handleNewItem,
    eventReceive: function(info) {
      console.log("Event received:", info.event);
      
      // Determine if this is a scheduled assessment being rescheduled
      const isRescheduling = info.event.extendedProps.isRescheduling;
      const assessmentId = info.event.id;
      
      // Create data for the API call
      const data = {
        assessment_id: assessmentId,
        assessment_date: info.event.start ? info.event.start.toISOString().split('T')[0] : null,
      };
      
      if (semester && semester.start_date) {
        const offsets = calculateWeekAndDayOffsets(info.event.start, semester.start_date);
        data.start_week = offsets.startWeek;
        data.start_day = offsets.startDay;
        data.end_week = offsets.endWeek;
        data.end_day = offsets.endDay;
      }
      
      console.log("Saving event with data:", data);
      
      // Add visual indicator that we're processing
      const loadingIndicator = document.createElement('div');
      loadingIndicator.className = 'event-loading';
      loadingIndicator.innerHTML = '<div class="loading-spinner"></div>';
      info.event.setProp('classNames', ['processing-drop']);
      
      // If it's already scheduled, we need to unschedule first then reschedule
      if (isRescheduling) {
        console.log("Rescheduling existing assessment:", assessmentId, "to date:", data.assessment_date);
        
        // We'll save the event directly instead of calling unscheduleEvent first
        saveEvent(data, info.event);
        
        // After successful save, we might want to update the UI
        // This will happen in the saveEvent function
        } else {
        // Regular scheduling of an unscheduled assessment
        saveEvent(data, info.event);
      }
    },
    eventRemove: function(info) {
      // Explicit remove actions, not drag-out
      console.log("Event removed:", info.event.id);
    },
    eventLeave: function(info) {
      console.log("Event left calendar:", info.event.id);
    },
    initialDate: semester && semester.start_date ? semester.start_date : undefined,
    eventClick: function(info) {
      // Only handle the click if it's not on the delete button
      // Button clicks are handled separately
    },
  });

  if (calendarEvents && calendarEvents.length > 0) {
    calendarEvents.forEach(event => {
      try {
        calendar.addEvent(event);
      } catch (e) {
        console.error(`Failed to add event ${event.id}:`, e);
      }
    });
    eventsLoaded = true;
  }

  try {
    console.log("Rendering calendar...");
    calendar.render();
    
    if (semester && semester.start_date) {
      console.log("Setting calendar initial date to semester start date:", semester.start_date);
      
      const currentDate = new Date();
      const semesterStartDate = new Date(semester.start_date);
      const semesterEndDate = new Date(semester.end_date);
      
      const savedDate = localStorage.getItem('calendarCurrentDate');
      const savedView = localStorage.getItem('calendarViewType');
      
      if (savedDate) {
        const savedDateObj = new Date(savedDate);
        if (savedDateObj >= semesterStartDate && savedDateObj <= semesterEndDate) {
        console.log("Restoring calendar to saved date:", savedDate);
          calendar.gotoDate(savedDateObj);
      } else {
          goToSemesterDate(calendar, currentDate, semesterStartDate, semesterEndDate);
        }
      } else {
        goToSemesterDate(calendar, currentDate, semesterStartDate, semesterEndDate);
      }
      
      if (savedView) {
        console.log("Restoring saved view type:", savedView);
        calendar.changeView(savedView);
      } else {
        calendar.changeView('dayGridMonth');
      }
    }
    
    function goToSemesterDate(calendar, currentDate, semesterStartDate, semesterEndDate) {
      if (currentDate >= semesterStartDate && currentDate <= semesterEndDate) {
        console.log("Current date is within semester, showing current month");
        calendar.gotoDate(currentDate);
      } 
      else if (currentDate < semesterStartDate) {
        console.log("Current date is before semester, showing semester start month");
        calendar.gotoDate(semesterStartDate);
      } 
      else {
        console.log("Current date is after semester, showing semester end month");
        calendar.gotoDate(semesterEndDate);
      }
    }
    
    // Apply visual styling to dates outside semester range
    const markDatesOutsideSemester = () => {
      if (semester && semester.start_date && semester.end_date) {
        const semesterStart = new Date(semester.start_date);
        const semesterEnd = new Date(semester.end_date);
        
        // Find all day cells in the calendar
        const dayCells = document.querySelectorAll('.fc-daygrid-day');
        
        dayCells.forEach(dayCell => {
          const dateAttr = dayCell.getAttribute('data-date');
          if (dateAttr) {
            const cellDate = new Date(dateAttr);
            
            // Check if date is outside semester range
            if (cellDate < semesterStart || cellDate > semesterEnd) {
              dayCell.classList.add('outside-semester');
            } else {
              dayCell.classList.remove('outside-semester');
            }
          }
        });
      }
    };
    
    // Initial application of outside-semester styling
    markDatesOutsideSemester();
    
    // Apply styling when month changes
    calendar.on('datesSet', function() {
      markDatesOutsideSemester();
      
      // Save current date and view for state preservation
      localStorage.setItem('calendarCurrentDate', calendar.getDate().toISOString());
      localStorage.setItem('calendarViewType', calendar.view.type);
    });
    
    // Ensure events are loaded by forcing a refetch after a short delay
    setTimeout(() => {
      console.log("Refreshing calendar events...");
      calendar.refetchEvents();
      
      // Highlight all scheduled assessments briefly to draw attention to them
      const calendarEvents = calendar.getEvents();
      console.log(`Calendar has ${calendarEvents.length} events loaded`);
      
      calendarEvents.forEach(event => {
        const eventEl = event.el;
        if (eventEl) {
          eventEl.style.transition = 'all 0.5s ease';
          eventEl.style.boxShadow = '0 0 8px 2px rgba(103, 78, 204, 0.6)';
          
          setTimeout(() => {
            eventEl.style.boxShadow = '';
          }, 1500);
        }
      });
    }, 300);
    
    // Make sure FullCalendar has initialized properly by checking its APIs
    console.log("Calendar API check:", {
      view: calendar.view ? calendar.view.type : "No view",
      date: calendar.getDate() ? calendar.getDate().toISOString() : "No date",
      events: calendar.getEvents().length
    });
    
  } catch (error) {
    console.error('Error rendering calendar:', error);
  }

  function loadSavedFilters() {
    console.log("Loading saved filters from localStorage");
    
    if (levelFilter && localStorage.getItem('calendarLevelFilter')) {
      levelFilter.value = localStorage.getItem('calendarLevelFilter');
      console.log("Loaded level filter:", levelFilter.value);
    }
    
    if (courseFilter && localStorage.getItem('calendarCourseFilter')) {
      const savedCourse = localStorage.getItem('calendarCourseFilter');
      const courseExists = Array.from(courseFilter.options).some(option => option.value === savedCourse);
      
      if (courseExists) {
        courseFilter.value = savedCourse;
        console.log("Loaded course filter:", courseFilter.value);
      } else {
        console.log("Saved course doesn't exist in options:", savedCourse);
      }
    }
    
    if (typeFilter && localStorage.getItem('calendarTypeFilter')) {
      typeFilter.value = localStorage.getItem('calendarTypeFilter');
      console.log("Loaded type filter:", typeFilter.value);
    }
    
    if (levelFilter && courseFilter && typeFilter) {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      
      console.log("Applying saved filters:", { selectedLevel, selectedCourse, selectedType });
      
      if (selectedLevel !== "0" || selectedCourse !== "all" || selectedType !== "all") {
        const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
        console.log("Initial filtered events count:", filteredEvents.length);
            updateCalendarEvents(calendar, filteredEvents, false);
      }
    }
  }

  setTimeout(loadSavedFilters, 300);

  if (levelFilter) {
    levelFilter.addEventListener("change", function () {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      
      console.log("Level filter changed:", selectedLevel);
      localStorage.setItem('calendarLevelFilter', selectedLevel);
      
      const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
      console.log(`Filtered events by level ${selectedLevel}:`, filteredEvents.length);
      updateCalendarEvents(calendar, filteredEvents);
    });
  }

  if (courseFilter) {
    courseFilter.addEventListener("change", function () {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      
      console.log("Course filter changed:", selectedCourse);
      localStorage.setItem('calendarCourseFilter', selectedCourse);
      
      const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
      console.log(`Filtered events by course ${selectedCourse}:`, filteredEvents.length);
      updateCalendarEvents(calendar, filteredEvents);
    });
  }

  if (typeFilter) {
    typeFilter.addEventListener("change", function () {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      
      console.log("Type filter changed:", selectedType);
      localStorage.setItem('calendarTypeFilter', selectedType);
      
      const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
      console.log(`Filtered events by type ${selectedType}:`, filteredEvents.length);
      updateCalendarEvents(calendar, filteredEvents);
    });
  }

  function filterEvents(level, courseCode, type) {
    let filteredEvents = scheduledAssessments || [];
    
    if (level !== "0") {
      filteredEvents = filteredEvents.filter(item => {
        return item.course_code && item.course_code.length >= 5 && item.course_code[4] === level;
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
      // Convert type to boolean or number based on the format in the data
      const isProctored = type === "1";
      filteredEvents = filteredEvents.filter(item => {
        // Handle both boolean and numeric representations of proctored
        if (typeof item.proctored === 'boolean') {
          return item.proctored === isProctored;
        } else {
          return (item.proctored == 1) === isProctored;
        }
      });
    }
    
    return filteredEvents;
  }

  function updateCalendarEvents(calendar, newEvents, removeExisting = true) {
    console.log("Updating calendar with filtered events:", newEvents.length);
    
    if (removeExisting) {
      calendar.removeAllEvents();
      console.log("Removed all existing events from calendar");
    }
    
    const updatedEvents = newEvents
      .filter(assessment => assessment.scheduled !== null && assessment.scheduled !== undefined)
      .map(assessment => {
        let startDate = formatDate(assessment.scheduled);
        if (!startDate) {
          console.log("Assessment has invalid date:", assessment);
          return null;
        }
        
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
    
    console.log("Filtered events for calendar:", updatedEvents.length);
    
      updatedEvents.forEach(event => {
      try {
        const existingEvent = calendar.getEventById(event.id);
        if (!existingEvent) {
          calendar.addEvent(event);
        }
      } catch (error) {
        console.error("Error adding event to calendar:", error, event);
      }
    });
    
    // Ensure events are rendered
    setTimeout(() => {
      calendar.render();
    }, 100);
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
    const event = info.event;
    const newDate = event.start;
    
    if (!semester || !semester.start_date || !semester.end_date) {
      info.revert();
      console.error('Semester date range not available');
      alert("Cannot reschedule assessment: No active semester found.");
      return;
    }
    
    const eventDate = newDate;
    const semesterStart = new Date(semester.start_date);
    const semesterEnd = new Date(semester.end_date);
    
    // Validate the drop is within the semester
    if (eventDate < semesterStart || eventDate > semesterEnd) {
      info.revert();
      alert("Cannot reschedule assessment: Date is outside the semester range.");
      return;
    }
    
    console.log("Rescheduling event via drag:", event.id, "to", newDate.toISOString().split('T')[0]);
    
    // Calculate week and day offsets
    const offsets = calculateWeekAndDayOffsets(newDate, semester.start_date);
    
    // Create data for saving
    const data = {
      assessment_id: event.id,
      assessment_date: newDate.toISOString().split('T')[0],
      start_week: offsets.startWeek,
      start_day: offsets.startDay,
      end_week: offsets.endWeek,
      end_day: offsets.endDay,
      is_rescheduling: true
    };
    
    // Add visual indicator that we're processing
    event.setProp('classNames', ['processing-drop']);
    
    // Store the original event reference in case we need to revert
    const originalEvent = event;
    
    // Save the event - treat this as a rescheduling
    saveEvent(data, event);
  }

  function handleNewItem(info) {
    return;
  }

  function saveEvent(data, event) {
    // Store the pending schedule data and event
    pendingScheduleData = data;
    pendingEvent = event;
    
    // First evaluate the clash value for this assessment date
    evaluateAssessmentClash(data.assessment_id, data.assessment_date);
  }

  function evaluateAssessmentClash(assessmentId, date) {
    // Show loading state
    document.body.classList.add('loading');
    
    fetch('/evaluate_assessment_date', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        assessment_id: assessmentId,
        date: date
      })
    })
    .then(response => response.json())
    .then(data => {
      document.body.classList.remove('loading');
      
      if (data.success) {
        displayClashEvaluation(data.evaluation);
      } else {
        // If error, just proceed with scheduling
        console.error('Failed to evaluate clash:', data.error);
        commitScheduleEvent();
      }
    })
    .catch(error => {
      document.body.classList.remove('loading');
      console.error('Error evaluating clash:', error);
      // On error, proceed with scheduling
      commitScheduleEvent();
    });
  }

  function displayClashEvaluation(data) {
    const clashValue = document.getElementById('avg-clash-value');
    const clashEvaluation = document.getElementById('clash-evaluation');
    const clashDetailsList = document.getElementById('clash-details-list');
    const highestClashValue = document.getElementById('highest-clash-value');
    
    // First, stop any pending redirect or action that might be in progress
    if (window.redirectInProgress) {
      clearTimeout(window.redirectInProgress);
      window.redirectInProgress = null;
    }
    
    // Set the average clash value with color coding
    if (data.average_clash_value !== undefined) {
      clashValue.textContent = Number(data.average_clash_value).toFixed(1);
      
      if (parseFloat(data.average_clash_value) <= 2.0) {
        clashValue.style.color = '#4cd964'; // green
      } else if (parseFloat(data.average_clash_value) <= 5.0) {
        clashValue.style.color = '#5e72e4'; // blue
      } else {
        clashValue.style.color = '#ff3b30'; // red
      }
    } else {
      clashValue.textContent = "0";
      clashValue.style.color = '#4cd964'; // green
    }
    
    // Set the highest clash value with color coding
    if (data.highest_clash_value !== undefined) {
      highestClashValue.textContent = Number(data.highest_clash_value).toFixed(1);
      
      if (parseFloat(data.highest_clash_value) <= 2.0) {
        highestClashValue.style.color = '#4cd964'; // green
      } else if (parseFloat(data.highest_clash_value) <= 5.0) {
        highestClashValue.style.color = '#5e72e4'; // blue
      } else {
        highestClashValue.style.color = '#ff3b30'; // red
      }
    } else {
      highestClashValue.textContent = "0";
      highestClashValue.style.color = '#4cd964'; // green
    }
    
    // Set the evaluation badge and class
    clashEvaluation.textContent = data.evaluation;
    clashEvaluation.className = 'evaluation-badge ' + data.evaluation.toLowerCase();
    
    // Clear and populate the details list
    clashDetailsList.innerHTML = '';
    
    if (data.details && data.details.length > 0) {
      data.details.forEach(detail => {
        const detailItem = document.createElement('div');
        detailItem.className = 'clash-details-item';
        
        // Format day impact based on the day_factor
        let dayImpact = '';
        if (detail.day_factor >= 1.0) {
          dayImpact = 'High impact (' + detail.days_difference + ' days difference)';
        } else if (detail.day_factor >= 0.6) {
          dayImpact = 'Medium impact (' + detail.days_difference + ' days difference)';
        } else if (detail.day_factor >= 0.3) {
          dayImpact = 'Low impact (' + detail.days_difference + ' days difference)';
        } else {
          dayImpact = 'Minimal impact (' + detail.days_difference + ' days difference)';
        }
        
        const assessmentDate = new Date(detail.assessment_date);
        const formattedDate = assessmentDate.toLocaleDateString();
        
        // Add proctored badge if assessment is proctored
        const proctoredBadge = detail.is_proctored ? 
          '<span class="badge proctored" style="margin-left: 10px;">Proctored</span>' : '';
        
        detailItem.innerHTML = `
          <div class="clash-course-info">
            <span class="clash-course-code">${detail.course_code}</span>
            <span class="clash-overlap">${detail.overlap_count} students overlap</span>
          </div>
          <div class="clash-assessment-info">
            <span class="clash-assessment-name">${detail.assessment_name}${proctoredBadge}</span>
            <span class="clash-assessment-date">${formattedDate}</span>
          </div>
          <div class="clash-contribution">
            <div class="clash-contrib-label">
              <span>${dayImpact}</span>
              <span class="clash-contrib-value">${Number(detail.clash_value).toFixed(1)} clash contribution</span>
            </div>
          </div>
        `;
        clashDetailsList.appendChild(detailItem);
      });
    } else {
      clashDetailsList.innerHTML = '<p>No overlapping assessments found.</p>';
    }
    
    // Show the modal and overlay with proper z-index
    const modal = document.getElementById('clash-modal');
    const overlay = document.getElementById('clash-modal-overlay');
    
    // Apply dark mode styling if needed
    if (isDarkModeActive()) {
      modal.classList.add('dark-mode');
      overlay.classList.add('dark-mode');
    } else {
      modal.classList.remove('dark-mode');
      overlay.classList.remove('dark-mode');
    }
    
    // Ensure the modal has high z-index to stay on top
    modal.style.zIndex = "2000";
    overlay.style.zIndex = "1999";
    
    modal.classList.remove('hidden');
    overlay.style.display = 'block';
    
    // Clear any existing event listeners
    const confirmBtn = document.getElementById('confirm-schedule-btn');
    const cancelBtn = document.getElementById('cancel-schedule-btn');
    const closeBtn = document.getElementById('close-clash-modal');
    
    // Remove old event listeners by cloning and replacing
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    newConfirmBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      // Close modal first
      document.getElementById('clash-modal').classList.add('hidden');
      document.getElementById('clash-modal-overlay').style.display = 'none';
      
      // Wait a moment to ensure UI updates before committing
      setTimeout(() => {
        commitScheduleEvent();
      }, 50);
      
      return false;
    });
    
    const newCancelBtn = cancelBtn.cloneNode(true);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    newCancelBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      document.getElementById('clash-modal').classList.add('hidden');
      document.getElementById('clash-modal-overlay').style.display = 'none';
      
      cancelScheduleEvent();
      return false;
    });
    
    const newCloseBtn = closeBtn.cloneNode(true);
    closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);
    newCloseBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      document.getElementById('clash-modal').classList.add('hidden');
      document.getElementById('clash-modal-overlay').style.display = 'none';
      
      cancelScheduleEvent();
      return false;
    });
    
    // Prevent clicks on the overlay from bubbling
    overlay.onclick = function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      document.getElementById('clash-modal').classList.add('hidden');
      document.getElementById('clash-modal-overlay').style.display = 'none';
      
      cancelScheduleEvent();
      return false;
    };
  }

  function closeClashModal() {
    const modal = document.getElementById('clash-modal');
    const overlay = document.getElementById('clash-modal-overlay');
    
    modal.classList.add('hidden');
    overlay.classList.add('hidden');
  }

  function cancelScheduleEvent() {
    // Revert the drag/drop UI without immediate page refresh
    if (pendingEvent) {
      if (pendingEvent.revert) {
        pendingEvent.revert();
      } else if (pendingEvent.remove) {
        pendingEvent.remove();
      }
      
      // Add visual feedback for the cancellation
      const cancelIndicator = document.createElement('div');
      cancelIndicator.style.position = 'fixed';
      cancelIndicator.style.top = '20px';
      cancelIndicator.style.left = '50%';
      cancelIndicator.style.transform = 'translateX(-50%)';
      cancelIndicator.style.padding = '10px 20px';
      cancelIndicator.style.backgroundColor = '#ff9500';
      cancelIndicator.style.color = 'white';
      cancelIndicator.style.borderRadius = '4px';
      cancelIndicator.style.zIndex = '9999';
      cancelIndicator.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
      cancelIndicator.innerText = 'Scheduling cancelled';
      
      document.body.appendChild(cancelIndicator);
      
      // Fade out and remove
      setTimeout(() => {
        cancelIndicator.style.opacity = '0';
        cancelIndicator.style.transition = 'opacity 0.5s ease';
        setTimeout(() => {
          document.body.removeChild(cancelIndicator);
        }, 500);
      }, 2000);
    }
    
    // Reset the pending data
    pendingScheduleData = null;
    pendingEvent = null;
  }

  function commitScheduleEvent() {
    if (!pendingScheduleData) {
      console.error('No pending schedule data to commit');
      return;
    }
    
    // Add visual feedback during API call
    if (pendingEvent && pendingEvent.setProp) {
      pendingEvent.setProp('classNames', ['processing-drop']);
    }
    
    // Send as JSON to our API endpoint
    fetch('/schedule_assessment_api', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(pendingScheduleData)
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Show success icon on the event
        if (pendingEvent && pendingEvent.setProp) {
          pendingEvent.setProp('classNames', ['scheduled-success']);
        }
        
        // Create success message that matches Flask flash messages
        const successMessage = document.createElement('div');
        successMessage.className = 'alert alert-success';
        successMessage.style.position = 'fixed';
        successMessage.style.top = '80px';
        successMessage.style.left = '50%';
        successMessage.style.transform = 'translateX(-50%)';
        successMessage.style.padding = '12px 20px';
        successMessage.style.borderRadius = '4px';
        successMessage.style.boxShadow = '0 4px 10px rgba(0,0,0,0.2)';
        successMessage.style.backgroundColor = '#4cd964';
        successMessage.style.color = 'white';
        successMessage.style.zIndex = '9999';
        successMessage.style.minWidth = '300px';
        successMessage.style.textAlign = 'center';
        successMessage.innerHTML = data.message || 'Assessment scheduled successfully';
        
        document.body.appendChild(successMessage);
        
        // Reset pending data
        pendingScheduleData = null;
        pendingEvent = null;
        
        // Refresh page after message is shown
        setTimeout(() => {
          successMessage.style.opacity = '0';
          successMessage.style.transition = 'opacity 0.3s ease';
          
          setTimeout(() => {
            window.location.reload();
          }, 300);
        }, 2000);
      } else {
        // Show error state and message
        if (pendingEvent && pendingEvent.setProp) {
          pendingEvent.setProp('classNames', ['scheduling-error']);
        }
        
        const errorMessage = document.createElement('div');
        errorMessage.className = 'alert alert-danger';
        errorMessage.style.position = 'fixed';
        errorMessage.style.top = '80px';
        errorMessage.style.left = '50%';
        errorMessage.style.transform = 'translateX(-50%)';
        errorMessage.style.padding = '12px 20px';
        errorMessage.style.borderRadius = '4px';
        errorMessage.style.boxShadow = '0 4px 10px rgba(0,0,0,0.2)';
        errorMessage.style.backgroundColor = '#ff3b30';
        errorMessage.style.color = 'white';
        errorMessage.style.zIndex = '9999';
        errorMessage.style.minWidth = '300px';
        errorMessage.style.textAlign = 'center';
        errorMessage.innerHTML = data.error || 'Error scheduling assessment';
        
        document.body.appendChild(errorMessage);
        
        // Reset pending data
        pendingScheduleData = null;
        pendingEvent = null;
        
        // Refresh after showing error
        setTimeout(() => {
          errorMessage.style.opacity = '0';
          errorMessage.style.transition = 'opacity 0.3s ease';
          
          setTimeout(() => {
            window.location.reload();
          }, 300);
        }, 2000);
      }
    })
    .catch(error => {
      console.error('Error scheduling assessment:', error);
      
      // Show error state and message
      if (pendingEvent && pendingEvent.setProp) {
        pendingEvent.setProp('classNames', ['scheduling-error']);
      }
      
      const errorMessage = document.createElement('div');
      errorMessage.className = 'alert alert-danger';
      errorMessage.style.position = 'fixed';
      errorMessage.style.top = '80px';
      errorMessage.style.left = '50%';
      errorMessage.style.transform = 'translateX(-50%)';
      errorMessage.style.padding = '12px 20px';
      errorMessage.style.borderRadius = '4px';
      errorMessage.style.boxShadow = '0 4px 10px rgba(0,0,0,0.2)';
      errorMessage.style.backgroundColor = '#ff3b30';
      errorMessage.style.color = 'white';
      errorMessage.style.zIndex = '9999';
      errorMessage.style.minWidth = '300px';
      errorMessage.style.textAlign = 'center';
      errorMessage.innerHTML = 'An error occurred while scheduling the assessment';
      
      document.body.appendChild(errorMessage);
      
      // Reset pending data
      pendingScheduleData = null;
      pendingEvent = null;
      
      // Refresh after showing error
      setTimeout(() => {
        errorMessage.style.opacity = '0';
        errorMessage.style.transition = 'opacity 0.3s ease';
        
        setTimeout(() => {
          window.location.reload();
        }, 300);
      }, 2000);
    });
  }

  function unscheduleEvent(eventId) {
    if (calendar) {
      localStorage.setItem('calendarViewType', calendar.view.type);
      localStorage.setItem('calendarCurrentDate', calendar.getDate().toISOString());
      
      const currentLevel = levelFilter ? levelFilter.value : "0";
      const currentCourse = courseFilter ? courseFilter.value : "all";
      const currentType = typeFilter ? typeFilter.value : "all";
      
      localStorage.setItem('calendarLevelFilter', currentLevel);
      localStorage.setItem('calendarCourseFilter', currentCourse);
      localStorage.setItem('calendarTypeFilter', currentType);
    }
    
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

  const filters = document.getElementById("filters");
  if (filters) {
    filters.style.marginBottom = '20px';
    
    const selects = filters.querySelectorAll('select');
    selects.forEach(select => {
      select.style.backgroundColor = 'var(--tertiary-color)';
      select.style.color = 'white';
      select.style.border = '1px solid var(--tertiary-color)';
      select.style.borderRadius = '4px';
      select.style.padding = '8px 12px';
      select.style.margin = '0 8px 8px 0';
      select.style.cursor = 'pointer';
      select.style.fontWeight = '500';
      
      const options = select.querySelectorAll('option');
      options.forEach(option => {
        option.style.backgroundColor = 'var(--tertiary-color)';
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function() {
    const collapsibleHeaders = document.querySelectorAll('.collapsible-header');
    
    collapsibleHeaders.forEach(header => {
      header.addEventListener('click', function() {
        this.classList.toggle('collapsed');
        const content = this.nextElementSibling;
        content.classList.toggle('collapsed');
      });
    });
    
    const showMoreBtn = document.getElementById('show-more-btn');
    const closePopupBtn = document.getElementById('close-popup-btn');
    const allAssessments = document.getElementById('all-assessments');
    const popupOverlay = document.querySelector('.popup-overlay');
    
    if (showMoreBtn) {
      showMoreBtn.addEventListener('click', function() {
        allAssessments.classList.remove('hidden');
        popupOverlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling behind popup
      });
    }
    
    if (closePopupBtn) {
      closePopupBtn.addEventListener('click', function() {
        allAssessments.classList.add('hidden');
        popupOverlay.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
      });
    }
    
    if (popupOverlay) {
      popupOverlay.addEventListener('click', function() {
        allAssessments.classList.add('hidden');
        popupOverlay.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
      });
    }
    
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && !allAssessments.classList.contains('hidden')) {
        allAssessments.classList.add('hidden');
        popupOverlay.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
      }
    });
  });

  function applyBlueBackgroundClass() {
    const assessmentItems = document.querySelectorAll('.assessment-item, .draggable-assessment');
    
    assessmentItems.forEach(item => {
      const style = window.getComputedStyle(item);
      const bgColor = style.backgroundColor;
      
      if (bgColor.includes('rgb(92, 70, 180)') || 
          bgColor.includes('rgb(94, 114, 228)') || 
          bgColor.includes('rgb(52, 152, 219)') ||
          item.style.backgroundColor === 'var(--tertiary-color)' ||
          item.style.backgroundColor === '#5e72e4') {
        item.classList.add('blue-bg');
      } else {
        item.classList.remove('blue-bg');
      }
    });
  }
  
  document.addEventListener('DOMContentLoaded', function() {
    applyBlueBackgroundClass();
    
    setTimeout(applyBlueBackgroundClass, 1000);
  });
  
  document.addEventListener('themeToggled', applyBlueBackgroundClass);

  // Check browser console for errors
  console.log("Draggable elements initialized:", 
    document.querySelectorAll(".draggable-assessment").length);

  // Function to show the unschedule confirmation dialog
  function showUnscheduleConfirmation(assessmentId, courseCode, assessmentName) {
    const overlay = document.getElementById('unschedule-overlay');
    const dialog = document.getElementById('unschedule-confirm');
    const nameSpan = document.getElementById('assessment-name-confirm');
    const idInput = document.getElementById('unschedule-assessment-id');
    
    // Set confirmation text and store the assessment ID
    nameSpan.textContent = `${courseCode}-${assessmentName}`;
    idInput.value = assessmentId;
    
    // Show the overlay and dialog
    overlay.style.display = 'block';
    dialog.style.display = 'block';
    
    // Add event listeners to buttons
    const confirmBtn = document.getElementById('confirm-unschedule-btn');
    const cancelBtn = document.getElementById('cancel-unschedule-btn');
    
    // Remove any existing listeners
    const newConfirmBtn = confirmBtn.cloneNode(true);
    const newCancelBtn = cancelBtn.cloneNode(true);
    
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    
    // Add new listeners
    newConfirmBtn.addEventListener('click', function() {
      // Close the dialog
      closeUnscheduleConfirmation();
      
      // Unschedule the assessment
      unscheduleEvent(idInput.value);
    });
    
    newCancelBtn.addEventListener('click', closeUnscheduleConfirmation);
    
    // Close when clicking on the overlay
    overlay.addEventListener('click', closeUnscheduleConfirmation);
    
    // Close on Escape key
    document.addEventListener('keydown', function escapeHandler(e) {
      if (e.key === 'Escape') {
        closeUnscheduleConfirmation();
        document.removeEventListener('keydown', escapeHandler);
      }
    });
  }

  // Function to close the unschedule confirmation dialog
  function closeUnscheduleConfirmation() {
    const overlay = document.getElementById('unschedule-overlay');
    const dialog = document.getElementById('unschedule-confirm');
    
    overlay.style.display = 'none';
    dialog.style.display = 'none';
  }

  // Add this function to check if dark mode is active
  function isDarkModeActive() {
    return document.body.classList.contains('dark-mode') || 
           document.documentElement.classList.contains('dark-mode') || 
           localStorage.getItem('darkMode') === 'true';
  }

  // Update showUnscheduleConfirm function to add dark mode class if needed
  function showUnscheduleConfirm(assessmentId, assessmentName) {
    const confirmDialog = document.getElementById('unschedule-confirm');
    const overlay = document.getElementById('unschedule-overlay');
    const nameSpan = document.getElementById('assessment-name-confirm');
    const idInput = document.getElementById('unschedule-assessment-id');
    
    if (confirmDialog && overlay && nameSpan && idInput) {
      nameSpan.textContent = assessmentName;
      idInput.value = assessmentId;
      
      // Apply dark mode if active
      if (isDarkModeActive()) {
        confirmDialog.classList.add('dark-mode');
        overlay.classList.add('dark-mode');
      } else {
        confirmDialog.classList.remove('dark-mode');
        overlay.classList.remove('dark-mode');
      }
      
      confirmDialog.style.display = 'block';
      overlay.style.display = 'block';
      
      // Add event listeners to buttons
      const confirmBtn = document.getElementById('confirm-unschedule-btn');
      const cancelBtn = document.getElementById('cancel-unschedule-btn');
      
      if (confirmBtn) {
        confirmBtn.onclick = function() {
          unscheduleEvent(assessmentId);
          confirmDialog.style.display = 'none';
          overlay.style.display = 'none';
        };
      }
      
      if (cancelBtn) {
        cancelBtn.onclick = function() {
          confirmDialog.style.display = 'none';
          overlay.style.display = 'none';
        };
      }
      
      // Close on overlay click
      overlay.onclick = function() {
        confirmDialog.style.display = 'none';
        overlay.style.display = 'none';
      };
    }
  }

  // Add theme change listener to update modals if they're visible
  document.addEventListener('themeToggled', function() {
    const isDark = isDarkModeActive();
    
    // Update the clash modal if visible
    const clashModal = document.getElementById('clash-modal');
    const clashOverlay = document.getElementById('clash-modal-overlay');
    
    if (clashModal && !clashModal.classList.contains('hidden')) {
      if (isDark) {
        clashModal.classList.add('dark-mode');
        clashOverlay.classList.add('dark-mode');
      } else {
        clashModal.classList.remove('dark-mode');
        clashOverlay.classList.remove('dark-mode');
      }
    }
    
    // Update unschedule confirm if visible
    const unscheduleConfirm = document.getElementById('unschedule-confirm');
    const unscheduleOverlay = document.getElementById('unschedule-overlay');
    
    if (unscheduleConfirm && unscheduleConfirm.style.display !== 'none') {
      if (isDark) {
        unscheduleConfirm.classList.add('dark-mode');
        unscheduleOverlay.classList.add('dark-mode');
      } else {
        unscheduleConfirm.classList.remove('dark-mode');
        unscheduleOverlay.classList.remove('dark-mode');
      }
    }
    
    // Update any active loading indicator
    const loadingIndicator = document.querySelector('.loading-indicator');
    if (loadingIndicator) {
      if (isDark) {
        loadingIndicator.classList.add('dark-mode');
      } else {
        loadingIndicator.classList.remove('dark-mode');
      }
    }
  });
}); 