import csv

def reformat_csv(input_file, output_file='reformatted_data.csv'):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        
        new_fieldnames = []
        for name in fieldnames:
            if name == 'summoner_spells':
                new_fieldnames.append('secondary_summoner_spell')
            else:
                new_fieldnames.append(name)
        
        writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
        writer.writeheader()

        for row in reader:
            # Reformat summoner_spells
            summoner_spells = row['summoner_spells']
            if summoner_spells.startswith('(') and summoner_spells.endswith(')'):
                summoner_spells = summoner_spells[1:-1]  # Remove parentheses
                spell1, spell2 = summoner_spells.split(', ')
                secondary_summoner_spell = int(spell2 if spell1 == '11' else spell1)
            else:
                secondary_summoner_spell = int(summoner_spells)

            # Reformat kill_details
            kill_details = row['kills_details']
            kill_details_reformatted = kill_details.replace(',', ';')  # Change comma to semicolon

            # Prepare the new row with the updated values
            new_row = { 
                'secondary_summoner_spell': secondary_summoner_spell,
                **{key: value for key, value in row.items() if key not in ['summoner_spells', 'kills_details']},
                'kills_details': kill_details_reformatted
            }

            writer.writerow(new_row)


reformat_csv('jungler_data.csv')
