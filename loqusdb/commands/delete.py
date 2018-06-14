# -*- coding: utf-8 -*-
import logging
import click
from datetime import datetime

from loqusdb.exceptions import CaseError
from loqusdb.utils.delete import delete as delete_command
from . import base_command

LOG = logging.getLogger(__name__)

@base_command.command('delete', short_help="Delete the variants of a family")
@click.argument('variant-file',
                    type=click.Path(exists=True),
                    metavar='<vcf_file>'
)
@click.option('-f', '--family-file',
                    type=click.Path(exists=True),
                    metavar='<ped_file>'
)
@click.option('-t' ,'--family-type', 
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']), 
                default='ped',
                help='If the analysis use one of the known setups, please specify which one.'
)
@click.option('-c' ,'--case-id', 
                type=str, 
                help='If a different case id than the one in ped file should be used'
)
@click.pass_context
def delete(ctx, variant_file, family_file, family_type, case_id):
    """Delete the variants of a case."""
    if not (family_file or case_id):
        LOG.error("Please provide a family file")
        ctx.abort()
    
    adapter = ctx.obj['adapter']

    start_deleting = datetime.now()
    try:
        delete_command(
            adapter=adapter, 
            variant_file=variant_file, 
            family_file=family_file, 
            family_type=family_type,
            case_id=case_id
        )
    except (CaseError, IOError) as error:
        LOG.warning(error)
        ctx.abort()
