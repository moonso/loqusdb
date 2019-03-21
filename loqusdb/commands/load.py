import os
import logging
import click

from pprint import pprint as pp

from datetime import datetime

from loqusdb.exceptions import (CaseError, VcfError)
from loqusdb.utils.load import load_database
from loqusdb.utils.vcf import (get_file_handle, check_vcf)

from . import base_command

LOG = logging.getLogger(__name__)

def validate_profile_threshold(ctx, param, value):
    if not (0 <= value <= 1):
        raise ValueError('threshold must be between 0-1')
    else:
        return value

@base_command.command('load', short_help="Load the variants of a family")
@click.option('--variant-file',
                    type=click.Path(exists=True),
                    metavar='<vcf_file>',
                    help="Load a VCF with SNV/INDEL Variants",
)
@click.option('--sv-variants',
                    type=click.Path(exists=True),
                    metavar='<sv_vcf_file>',
                    help="Load a VCF with Structural Variants",
)
@click.option('-f', '--family-file',
                    type=click.Path(exists=True),
                    metavar='<ped_file>'
)
@click.option('-t' ,'--family-type',
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']),
                default='ped',
                show_default=True,
                help='If the analysis use one of the known setups, please specify which one.'
)
@click.option('-c' ,'--case-id',
                type=str,
                help='If a different case id than the one in ped file should be used'
)
@click.option('-s' ,'--skip-case-id',
                is_flag=True,
                show_default=True,
                help='Do not store case information on variants'
)
@click.option('--ensure-index',
                is_flag=True,
                help='Make sure that the indexes are in place'
)
@click.option('--gq-treshold',
                default=20,
                show_default=True,
                help='Treshold to consider variant'
)
@click.option('--max-window', '-m',
                default=2000,
                show_default=True,
                help='Specify the maximum window size for svs'
)
@click.option('--check-profile',
                is_flag=True,
                help='Apply sample profiling for the samples in the vcf'
)
@click.option('--profile-threshold',
                type=float,
                default=0.9,
                callback=validate_profile_threshold,
                help='Threshold for profile check (0-1)'
)
@click.pass_context
def load(ctx, variant_file, sv_variants, family_file, family_type, skip_case_id, gq_treshold,
         case_id, ensure_index, max_window, check_profile, profile_threshold):
    """Load the variants of a case

    A variant is loaded if it is observed in any individual of a case
    If no family file is provided all individuals in vcf file will be considered.
    """
    if not (family_file or case_id):
        LOG.warning("Please provide a family file or a case id")
        ctx.abort()

    if not (variant_file or sv_variants):
        LOG.warning("Please provide a VCF file")
        ctx.abort()

    variant_path = None
    if variant_file:
        variant_path = os.path.abspath(variant_file)

    variant_sv_path = None
    if sv_variants:
        variant_sv_path = os.path.abspath(sv_variants)

    adapter = ctx.obj['adapter']

    start_inserting = datetime.now()

    try:
        nr_inserted = load_database(
            adapter=adapter,
            variant_file=variant_path,
            sv_file=variant_sv_path,
            family_file=family_file,
            family_type=family_type,
            skip_case_id=skip_case_id,
            case_id=case_id,
            gq_treshold=gq_treshold,
            max_window=max_window,
            check_profile=check_profile,
            profile_threshold=profile_threshold
        )
    except (SyntaxError, CaseError, IOError) as error:
        LOG.warning(error)
        ctx.abort()

    LOG.info("Nr variants inserted: %s", nr_inserted)
    LOG.info("Time to insert variants: {0}".format(
                datetime.now() - start_inserting))

    if ensure_index:
        adapter.ensure_indexes()
    else:
        adapter.check_indexes()
