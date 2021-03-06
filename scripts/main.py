import os
import shutil
import glob
import datetime
import dives
import events
import vitals
import kml

# Time range for the analysis
begin = datetime.datetime(2017, 1, 1)
end = datetime.datetime(2100, 1, 1)

# Boolean set to true in order to delete every processed data and redo everything
redo = False

# Plot interactive figures in HTML format for acoustic events
# WARNING: Plotly files takes a lot of memory so commented by default
events_plotly = True


def main():
    # Set working directory in "scripts"
    if "scripts" in os.listdir("."):
        os.chdir("scripts")

    # Create processed directory if it doesn't exist
    if not os.path.exists("../processed/"):
        os.mkdir("../processed/")

    # Search Mermaid floats
    mfloats = [p.split("/")[-1][:-4] for p in glob.glob("../server/*.vit")]

    # For each Mermaid float
    for mfloat in mfloats:
        print ""
        print "> " + mfloat

        # Set the path for the float
        mfloat_path = "../processed/" + mfloat + "/"

        # Delete the directory if the redo flag is true
        if redo and os.path.exists(mfloat_path):
            shutil.rmtree(mfloat_path)

        # Create directory for the float
        if not os.path.exists(mfloat_path):
            os.mkdir(mfloat_path)

        # Copy appropriate files in the directory
        for f in glob.glob("../server/" + mfloat + "*"):
            shutil.copy(f, mfloat_path)
        for f in glob.glob("../server/" + mfloat[-4:] + "_*"):
            shutil.copy(f, mfloat_path)

        # Build list of all mermaid events recorded by the float
        mevents = events.Events(mfloat_path)

        # Process data for each dive
        mdives = dives.get_dives(mfloat_path, mevents)
        for dive in mdives:
            # Check the begin and end date
            if dive.date < begin or dive.date > end:
                continue
            # Create the directory
            if not os.path.exists(dive.export_path):
                os.mkdir(dive.export_path)
            # Generate log
            dive.generate_datetime_log()
            # Generate mermaid environment file
            dive.generate_mermaid_environment_file()
            # Generate dive plot
            dive.generate_dive_plotly()

        # Compute clock drift correction for each event
        for dive in mdives:
            dive.correct_events_clock_drift()

        # Compute location of mermaid float for each event (because the station is moving)
        # the algorithm use gps information in the next dive to estimate surface drift
        i = 0
        while i < len(mdives)-1:
            mdives[i].compute_events_station_location(mdives[i+1])
            i += 1

        # Generate plot and sac files
        for dive in mdives:
            dive.generate_events_plot()
            if events_plotly:
                dive.generate_events_plotly()
            dive.generate_events_sac()

        # Plot vital data
        kml.generate(mfloat_path, mfloat, mdives)
        vitals.plot_battery_voltage(mfloat_path, mfloat + ".vit", begin, end)
        vitals.plot_internal_pressure(mfloat_path, mfloat + ".vit", begin, end)
        vitals.plot_pressure_offset(mfloat_path, mfloat + ".vit", begin, end)

        # Clean directories
        for f in glob.glob(mfloat_path + "/" + mfloat + "*"):
            os.remove(f)
        for f in glob.glob(mfloat_path + "/" + mfloat[-2:] + "_*.LOG"):
            os.remove(f)
        for f in glob.glob(mfloat_path + "/" + mfloat[-2:] + "_*.MER"):
            os.remove(f)


if __name__ == "__main__":
    main()
