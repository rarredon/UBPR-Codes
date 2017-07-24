#!/bin/python

import sys
import csv

concept_labels = ['DESCRIPTION', 'NARRATIVE', 'FORMULA']


def main(argv):
    infile = argv[1]
    outfile = argv[2]
    reffile = outfile[:-4] + '_reference' + outfile[-4:]

    # Write header to reference file
    with open(reffile, 'w', newline='') as ref:
        refwriter = csv.writer(ref)
        refwriter.writerow(['REFERENCING SECTION',
                            'REFERENCING SECTION NUMBER',
                            'REFERENCED CONCEPT',
                            'DESCRIPTION',
                            'NARRATIVE',
                            'FORMULA'])

    # Create the outfile
    with open(infile, 'r') as guide, open(outfile, 'w', newline='') as csvfile:
        # Initialize and create header
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['SECTION', 'SECTION NUMBER', 'SUBSECTION',
                            'CONCEPT ID', 'CONCEPT NAME',
                            'DESCRIPTION', 'NARRATIVE', 'FORMULA'])

        # Get to the first section
        line = guide.readline().strip()
        lineno = 1
        while line != 'SECTION':
            line = guide.readline().strip()
            lineno += 1

        status = 'SECTION'  # a.k.a. Where are we?
        for line in guide:
            line = line.strip()
            lineno += 1

            # This block of logic is to double check current `status`
            if line == 'SECTION':
                sectionline = guide.readline().strip()
                sectionnoline = guide.readline().strip()
                sectionnoline += 'F' if 'Fiduciary' in sectionline else ''
                lineno += 2
                if sectionline != section or sectionnoline != sectionno:
                    # Update section
                    section = sectionline
                    sectionno = sectionnoline
                    status = 'SUBSECTION'

                    # Write out the last concept from previous section
                    csvwriter.writerow([section, sectionno, subsection,
                                        conceptid, conceptname,
                                        description, narrative, formula])

                # Continue with SUBSECTION or continue with previous status
                continue
            elif line == 'REFERENCE':
                # Write out last concept from current section, build reference
                csvwriter.writerow([section, sectionno, subsection,
                                    conceptid, conceptname,
                                    description, narrative, formula])

                section, sectionno, lineno = \
                    build_reference(reffile, guide, section, sectionno, lineno)
                if section is None and sectionno is None and lineno is None:
                    break
                status = 'SUBSECTION'
                continue
            elif status == 'CONCEPTINFO':
                assert line in concept_labels, \
                    'Thought we were in concept info (%d), NOPE' % lineno
                status = line
                continue
            elif line in concept_labels:
                status = line
                continue
            # Note that we're assuming every concept ends with FORMULA
            elif status == 'FORMULA':
                # If line begins with int, let's assume new subsection
                try:
                    if int(line.split()[0]) == (subsectionno + 1):
                        status = 'SUBSECTION'  # New subsection on no error
                except ValueError:
                    # If line begins with float, let's assume new concept
                    try:
                        newconceptno = float(line.split()[0])
                        if newconceptno == (conceptno + 0.1):
                            status = 'NEWCONCEPT'  # New concept on no error
                    except ValueError:
                        pass  # Continuing with formula

                if status != 'FORMULA':  # previous concept is ready to write
                    csvwriter.writerow([section, sectionno, subsection,
                                        conceptid, conceptname,
                                        description, narrative, formula])
            # END IF (status checking logic)

            # Now that status is double checked, react accordingly
            if status == 'SECTION':  # Get section
                section = line
                status = 'SECTIONNO'
            elif status == 'SECTIONNO':  # Get section number
                sectionno = line
                sectionno += 'F' if 'Fiduciary' in section else ''
                status = 'SUBSECTION'
            elif status == 'SUBSECTION':  # Get subsection
                line = line.split()
                assert int(line[0]), \
                    'Thought we were in subsection (%d), NOPE' % lineno
                subsectionno = int(line[0])
                subsection = ' '.join(line[1:])
                status = 'NEWCONCEPT'
            elif status == 'NEWCONCEPT':  # Get concept ID and concept name
                description = ''
                narrative = ''
                formula = ''
                line = line.split()
                assert len(line) == 2 and float(line[0]), \
                    'Thought we were in newconcept (%d), NOPE' % lineno
                conceptno = float(line[0])
                conceptid = sectionno + '.' + line[0]
                conceptname = line[1]
                status = 'CONCEPTINFO'
            elif status == 'DESCRIPTION':
                description += line
            elif status == 'NARRATIVE':
                narrative += line
            elif status == 'FORMULA':
                formula += line
            # END IF (reaction to status)


def build_reference(outfile, guide, section, sectionno, lineno):
    with open(outfile, 'a', newline='') as f:
        refwriter = csv.writer(f)
        status = 'NEWCONCEPT'
        for line in guide:
            line = line.strip()
            lineno += 1

            # Double check the status
            if line == 'SECTION':
                sectionline = guide.readline().strip()
                sectionnoline = guide.readline().strip()
                sectionnoline += 'F' if 'Fiduciary' in sectionline else ''
                lineno += 2
                if sectionline != section or sectionnoline != sectionno:
                    # New section, write last concept, return control to caller
                    refwriter.writerow([section, sectionno, conceptname,
                                        description, narrative, formula])
                    return sectionline, sectionnoline, lineno
                # Continue with SUBSECTION or continue with previous status
                continue
            elif line in concept_labels:
                status = line
                continue
            # Note that we're assuming every concept ends with FORMULA
            elif status == 'FORMULA':
                if len(line) == 8 and line.startswith('UBPR'):
                    status = 'NEWCONCEPT'

                if status != 'FORMULA':
                    refwriter.writerow([section, sectionno, conceptname,
                                        description, narrative, formula])

            # Get concept info
            if status == 'NEWCONCEPT':
                description = ''
                narrative = ''
                formula = ''
                conceptname = line
            elif status == 'DESCRIPTION':
                description += line
            elif status == 'NARRATIVE':
                narrative += line
            elif status == 'FORMULA':
                formula += line
        # Executed at the end of the for loop, i.e., end of the file
        return None, None, None


if __name__ == '__main__':
    main(sys.argv)
