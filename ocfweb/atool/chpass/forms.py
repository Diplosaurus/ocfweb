import ocflib.account.search as search
import ocflib.ucb.groups as groups
from django import forms

from ocfweb.atool.constants import TEST_OCF_ACCOUNTS
from ocfweb.atool.constants import TESTER_CALNET_UIDS


def _get_accounts_signatory_for(calnet_uid):
    def flatten(lst):
        return [item for sublist in lst for item in sublist]

    group_accounts = flatten(map(
        lambda group: group['accounts'],
        groups.groups_by_student_signat(calnet_uid).values()))

    # sanity check since we don't trust CalLink API that much:
    # if >= 10 groups, can't change online, sorry
    assert len(group_accounts) < 10, 'should be less than 10 group accounts'

    return group_accounts


def get_authorized_accounts_for(calnet_uid):
    accounts = search.users_by_calnet_uid(calnet_uid) + \
        _get_accounts_signatory_for(calnet_uid)

    if calnet_uid in TESTER_CALNET_UIDS:
        # these test accounts don't have to exist in in LDAP
        accounts.extend(TEST_OCF_ACCOUNTS)

    return accounts


class ChpassForm(forms.Form):

    def __init__(self, ocf_accounts, calnet_uid, *args, **kwargs):
        super(ChpassForm, self).__init__(*args, **kwargs)
        self.calnet_uid = calnet_uid
        self.fields['ocf_account'] = forms.ChoiceField(choices=[
            (x, x) for x in ocf_accounts],
            label='OCF account')
        self.fields.keyOrder = [
            'ocf_account',
            'new_password',
            'confirm_password'
        ]

    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label='New password',
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label='Confirm password',
    )

    def clean_ocf_account(self):
        data = self.cleaned_data['ocf_account']
        if not search.user_exists(data):
            raise forms.ValidationError('OCF user account does not exist.')

        ocf_accounts = get_authorized_accounts_for(self.calnet_uid)

        if data not in ocf_accounts:
            raise forms.ValidationError(
                'OCF user account and CalNet UID mismatch.')

        return data

    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Your passwords don't match.")
        return confirm_password