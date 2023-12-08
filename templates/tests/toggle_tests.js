
/*
To run these tests, do the following, add testToggle() to the eventListeners
for the dropdown so that this function runs every time a user uses the toggle.
If the console raises errors, then the tests do not pass.
*/

function testToggle() {
    const currTheme = document.documentElement.getAttribute('data-bs-theme');

    // SCENARIO 1: dark mode should change to light mode
    if (currTheme === 'dark') {
        // check if data-bs-theme attribute actually changes to dark mode
        toggleTheme('light');
        assert(document.documentElement.getAttribute('data-bs-theme') === 'light');

        // check if the text label correctly switches
        assert(document.getElementById('theme-label').innerHTML === 'Light')

        // check if the correct option is highlighted in the dropdown
        changeActiveStatus(lightMode, darkMode);
        assert('active' in document.getElementById('light-dropdown').getAttribute('class'))
        assert(!('active' in document.getElementById('dark-dropdown').getAttribute('class')))
    }

    // SCENARIO 2: dark mode should remain if "dark" is selected
    if (currTheme === 'dark') {
        toggleTheme('dark');
        assert(document.documentElement.getAttribute('data-bs-theme') === 'dark');

        assert(document.getElementById('theme-label').innerHTML === 'Dark')

        changeActiveStatus(lightMode, darkMode);
        assert(!('active' in document.getElementById('light-dropdown').getAttribute('class')))
        assert('active' in document.getElementById('dark-dropdown').getAttribute('class'))
    }
    
        // SCENARIO 3: light mode should change to dark mode
    if (currTheme === 'light') {
        toggleTheme('dark');
        assert(document.documentElement.getAttribute('data-bs-theme') === 'dark');

        assert(document.getElementById('theme-label').innerHTML === 'Dark')

        changeActiveStatus(darkMode, lightMode);
        assert('active' in document.getElementById('dark-dropdown').getAttribute('class'))
        assert(!('active' in document.getElementById('light-dropdown').getAttribute('class')))
    }

    // SCENARIO 4: light mode should remain if "light" is selected
    if (currTheme === 'light') {
        toggleTheme('light');
        assert(document.documentElement.getAttribute('data-bs-theme') === 'light');

        assert(document.getElementById('theme-label').innerHTML === 'Light')

        changeActiveStatus(lightMode, lightMode);
        assert('active' in document.getElementById('light-dropdown').getAttribute('class'))
        assert(!('active' in document.getElementById('dark-dropdown').getAttribute('class')))
    }
}
