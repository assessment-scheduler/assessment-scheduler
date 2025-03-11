$(document).ready(function(){
    console.log(course_assessments);
})

const cardContainer = document.getElementById('card_container');

course_assessments.forEach(courseData => {
    const course = courseData.course;
    const assessments = courseData.assessments;
    
    assessments.forEach(assessment => {
        const card = document.createElement('div');
        card.classList.add('card');
        card.setAttribute('data-course-code', course.code);
        
        const courseDetails = document.createElement('div');
        courseDetails.classList.add('course-details');
        const assessmentInfo = document.createElement('div');
        assessmentInfo.classList.add('assessment-info');
        const actions = document.createElement('div');
        actions.classList.add('actions');

        const courseCodeLabel = document.createElement('p');
        courseCodeLabel.classList.add('card-label');
        courseCodeLabel.textContent = 'Course Code';
        const courseCode = document.createElement('p');
        courseCode.classList.add('course-code');
        courseCode.textContent = course.code;

        const courseAssessmentLabel = document.createElement('p');
        courseAssessmentLabel.classList.add('card-label');
        courseAssessmentLabel.textContent = 'Assessment Name';
        const assessmentType = document.createElement('p');
        assessmentType.classList.add('assessment-type');
        assessmentType.textContent = assessment.name;

        const caNumLabel = document.createElement('p');
        caNumLabel.classList.add('card-label');
        caNumLabel.textContent = 'Assessment ID';
        const caNum = document.createElement('p');
        caNum.classList.add('assessment-id');
        caNum.textContent = assessment.a_id;

        const categoryLabel = document.createElement('p');
        categoryLabel.classList.add('card-label');
        categoryLabel.textContent = 'Category';
        const category = document.createElement('p');
        category.classList.add('category');
        category.textContent = assessment.category;

        const percentageLabel = document.createElement('p');
        percentageLabel.classList.add('card-label');
        percentageLabel.textContent = 'Percentage';
        const percentage = document.createElement('p');
        percentage.classList.add('percentage');
        percentage.textContent = assessment.percentage + '%';

        const startWeekLabel = document.createElement('p');
        startWeekLabel.classList.add('card-label');
        startWeekLabel.textContent = 'Start Week';
        const startWeek = document.createElement('p');
        startWeek.classList.add('start-week');
        startWeek.textContent = 'Week ' + assessment.start_week + ', Day ' + assessment.start_day;

        const endWeekLabel = document.createElement('p');
        endWeekLabel.classList.add('card-label');
        endWeekLabel.textContent = 'End Week';
        const endWeek = document.createElement('p');
        endWeek.classList.add('end-week');
        endWeek.textContent = 'Week ' + assessment.end_week + ', Day ' + assessment.end_day;
        
        const proctoredLabel = document.createElement('p');
        proctoredLabel.classList.add('card-label');
        proctoredLabel.textContent = 'Proctored';
        const proctored = document.createElement('p');
        proctored.classList.add('proctored');
        proctored.textContent = assessment.proctored ? 'Yes' : 'No';

        // Create action links (modify and delete can be replaced with actual functionality)
        const modifyLink = document.createElement('button');
        modifyLink.textContent = 'Modify';
        modifyLink.addEventListener('click', function() {
            window.location.href = `/update_assessment/${assessment.a_id}`;
        });
        const deleteLink = document.createElement('button');
        deleteLink.textContent = 'Delete';
        deleteLink.classList.add('delete_btn')
        deleteLink.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to delete this assessment?')) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/delete_assessment/${assessment.a_id}`;
                document.body.appendChild(form);
                form.submit();
            }
        });
    

        courseDetails.appendChild(courseCodeLabel);
        courseDetails.appendChild(courseCode);
        assessmentInfo.appendChild(courseAssessmentLabel);
        assessmentInfo.appendChild(assessmentType);
        assessmentInfo.appendChild(categoryLabel);
        assessmentInfo.appendChild(category);
        assessmentInfo.appendChild(percentageLabel);
        assessmentInfo.appendChild(percentage);
        assessmentInfo.appendChild(startWeekLabel);
        assessmentInfo.appendChild(startWeek);
        assessmentInfo.appendChild(endWeekLabel);
        assessmentInfo.appendChild(endWeek);
        assessmentInfo.appendChild(proctoredLabel);
        assessmentInfo.appendChild(proctored);
        actions.appendChild(modifyLink);
        actions.appendChild(deleteLink);
        card.appendChild(courseDetails);
        card.appendChild(assessmentInfo);
        card.appendChild(actions);
        
        // Append the card to the card container
        cardContainer.appendChild(card);
    });
});