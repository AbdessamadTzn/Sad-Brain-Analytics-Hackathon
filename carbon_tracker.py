from codecarbon import OfflineEmissionsTracker
import pandas as pd


tracker = OfflineEmissionsTracker(
    project_name="Hackathon 2 - Data/IA - Groupe 5 - ",
    output_dir='./emissions',
    measure_power_secs=10,
    save_to_file=True,
    allow_multiple_runs=True,
    country_iso_code="FRA",
    region="",
    log_level="ERROR"  # Suppress console output
)

def start_tracker():
    tracker.start()

def stop_tracker():
    tracker.stop()

def update_project_name(new_project_name):
    global tracker
    tracker.stop()  # Stop the current tracker if it's running
    tracker = OfflineEmissionsTracker(
        project_name = f"Hackathon 2 - Data/IA - Groupe 5 - {new_project_name}",
        output_dir='./emissions',
        measure_power_secs=10,
        save_to_file=True,
        allow_multiple_runs=True,
        country_iso_code="FRA",
        region="Auvergne Rhône-Alpes",
        log_level="ERROR"  # Suppress console output
    )
    tracker.start()  # Start the new tracker with the updated experiment name



def show_metrics():
    # Load emissions data from CSV file
    emissions_df = pd.read_csv('./emissions/emissions.csv')
    if not emissions_df.empty:

        if emissions_df['project_name'].unique().size >= 1:
            print("Total Emissions per Project:")
            grouped_emissions_df = emissions_df.groupby('project_name')

            for project_name, group in grouped_emissions_df:
                total_emissions = group['emissions'].sum()
                print(f"\nProject Name: {project_name}")
                print(f"Total Emissions: {total_emissions:.2f} kg CO2")

                # Calculate the difference between first and last timestamp
                first_timestamp = pd.to_datetime(group['timestamp'].min())
                last_timestamp = pd.to_datetime(group['timestamp'].max())
                duration = last_timestamp - first_timestamp
                run_duration = pd.to_timedelta(group['duration'].sum(), unit='s')
                print(f"Run Duration: {run_duration.days} days, {run_duration.seconds // 3600:02} hours, {(run_duration.seconds // 60) % 60:02} minutes and {run_duration.seconds % 60:02} seconds")
                print(f"Total Duration: {duration.days} days, {duration.seconds // 3600:02} hours, {(duration.seconds // 60) % 60:02} minutes and {duration.seconds % 60:02} seconds")

                print(f"Energy Consumed: {group['energy_consumed'].sum():.2f} kWh")
                print(f"CPU Power: {group['cpu_power'].sum():.2f} W")
                print(f"GPU Power: {group['gpu_power'].sum():.2f} W")
                print(f"RAM Power: {group['ram_power'].sum():.2f} W")

                # Everyday consumption equivalences
                total_emissions_tonnes = total_emissions / 1000  # Convert kg to tonnes

                # Travel equivalences
                travel_equivalences = {
                    "driving a thermal car": total_emissions_tonnes * 4596,
                    "flying by plane": total_emissions_tonnes * 4348,
                    "driving an electric car": total_emissions_tonnes * 9671,
                    "traveling by TGV": total_emissions_tonnes * 423729
                }

                print("\nTravel Equivalences:")
                for activity, km in travel_equivalences.items():
                    if km > 0.0001:
                        print(f"  - {activity}: {km:.4f} km")

                # Production equivalences
                production_equivalences = {
                    "televisions (40 to 49 inches)": total_emissions_tonnes * 2.4,
                    "air conditioners": total_emissions_tonnes * 2.9,
                    "laptops": total_emissions_tonnes * 6,
                    "smartphones": total_emissions_tonnes * 32,
                    "jeans": total_emissions_tonnes * 42,
                    "cotton t-shirts": total_emissions_tonnes * 163,
                    "liters of bottled water": total_emissions_tonnes * 2209
                }

                print("\nProduction Equivalences:")
                for product, quantity in production_equivalences.items():
                    if quantity > 0.0001:
                        print(f"  - {product}: {quantity:.4f}")

                # Consumption equivalences
                consumption_equivalences = {
                    "years of gas heating": total_emissions_tonnes * 0.2,
                    "years of electric heating": total_emissions_tonnes * 1.5,
                    "beef meals": total_emissions_tonnes * 138,
                    "vegetarian meals": total_emissions_tonnes * 1962,
                    "hours of video streaming": total_emissions_tonnes * 15621
                }

                print("\nConsumption Equivalences:")
                for activity, value in consumption_equivalences.items():
                    if value > 0.0001:
                        print(f"  - {activity}: {value:.4f}")

                # Average French carbon footprint: ~8.9 tons of CO2 per year
                average_french_footprint_tons = 8.9
                footprint_percentage = (total_emissions_tonnes / average_french_footprint_tons) * 100
                if footprint_percentage > 0.0001:
                    print(f"Percentage of the average French annual carbon footprint: {footprint_percentage:.4f}%")
    



    else:
        print("No emissions data available. Make sure the tracker has been started and stopped.")